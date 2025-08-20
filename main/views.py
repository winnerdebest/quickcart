from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import *
from django.views.decorators.http import require_GET
import json
from django.views.decorators.csrf import csrf_exempt

def products(request):
    # Check if it's an AJAX request (JSON requested) or if 'page' parameter exists
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.headers.get('Accept', '').find('application/json') > -1 or
        'page' in request.GET
    )
    
    if is_ajax:
        # AJAX request for infinite scroll
        page = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')
        
        products = Product.objects.all()
        if search_query:
            products = products.filter(name__icontains=search_query)
            
        paginator = Paginator(products, 12)  
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': product.id,
                    'name': product.name,
                    'slug': product.slug,
                    'description': product.description,
                    'price': str(product.price),
                    'image': product.image.url if product.image else '',
                }
                for product in page_obj
            ],
            'has_next': page_obj.has_next()
        }
        return JsonResponse(data)
    
    # Initial page load
    return render(request, 'main/products.html')


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    return render(request, "main/detail.html", {"product": product})

"""def generate_payment_link(order_id, total):
    # Replace with actual payment gateway integration
    return f"https://pay.example.com/order/{order_id}?amount={total}" """

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.urls import reverse
import json
import requests
import uuid
from decimal import Decimal
from .models import Product, Order, OrderItem


def checkout_view(request):
    """Render the checkout page"""
    return render(request, 'main/checkout.html')


@csrf_exempt
@require_http_methods(["POST"])
def process_checkout(request):
    """Process the checkout form and create order"""
    try:
        data = json.loads(request.body)
        
        # Extract form data
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()
        items = data.get('items', [])
        
        # Validate required fields
        if not all([full_name, email, phone, address]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        if not items:
            return JsonResponse({'error': 'No items in cart'}, status=400)
        
        # Create order
        order = Order.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            status='pending'
        )
        
        # Process order items and calculate total
        total_amount = Decimal('0.00')
        order_items_data = []
        
        for item_data in items:
            try:
                product = get_object_or_404(Product, id=item_data['id'])
                quantity = int(item_data['quantity'])
                
                if quantity <= 0:
                    raise ValueError("Invalid quantity")
                
                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                
                item_total = product.price * quantity
                total_amount += item_total
                
                order_items_data.append({
                    'name': product.name,
                    'quantity': quantity,
                    'price': str(product.price),
                    'total': str(item_total)
                })
                
            except (Product.DoesNotExist, ValueError, KeyError) as e:
                # Clean up the order if there's an error
                order.delete()
                return JsonResponse({'error': f'Invalid item data: {str(e)}'}, status=400)
        
        # Generate payment link with Flutterwave
        payment_link = create_flutterwave_payment_link(request, order, total_amount)
        
        if not payment_link:
            order.delete()
            return JsonResponse({'error': 'Failed to create payment link'}, status=500)
        
        # Return order confirmation data
        response_data = {
            'order_id': order.id,
            'items': order_items_data,
            'total': str(total_amount),
            'payment_link': payment_link,
            'customer': {
                'name': full_name,
                'email': email,
                'phone': phone,
                'address': address
            }
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


def create_flutterwave_payment_link(request, order, amount):
    """Create a payment link using Flutterwave API"""
    
    # Flutterwave configuration - Add these to your settings.py
    FLUTTERWAVE_SECRET_KEY = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
    FLUTTERWAVE_PUBLIC_KEY = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', '')
    
    if not FLUTTERWAVE_SECRET_KEY:
        print("Warning: FLUTTERWAVE_SECRET_KEY not configured")
        return None
    
    # Generate unique transaction reference
    tx_ref = f"order_{order.id}_{uuid.uuid4().hex[:8]}"
    
    # Payment data
    payment_data = {
        "tx_ref": tx_ref,
        "amount": str(amount),
        "currency": "NGN",
        "redirect_url": request.build_absolute_uri(reverse('payment_callback')),
        "customer": {
            "email": order.email,
            "phonenumber": order.phone,
            "name": order.full_name
        },
        "customizations": {
            "title": "QuickCart Payment",
            "description": f"Payment for Order #{order.id}",
            "logo": ""  # Add your logo URL here
        },
        "meta": {
            "order_id": order.id
        }
    }
    
    headers = {
        'Authorization': f'Bearer {FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            'https://api.flutterwave.com/v3/payments',
            json=payment_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                 #Store transaction reference in order (you might want to add this field to your Order model)
                order.transaction_ref = tx_ref
                order.save()
                
                return result['data']['link']
        
        print(f"Flutterwave API Error: {response.status_code} - {response.text}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Flutterwave Request Error: {str(e)}")
        return None


@csrf_exempt
def payment_callback(request):
    """Handle payment callback from Flutterwave"""

    if request.method == 'GET':
        # Handle redirect callback
        status = request.GET.get('status')
        tx_ref = request.GET.get('tx_ref')
        transaction_id = request.GET.get('transaction_id')
        payment_type = request.GET.get('payment_type')  # If available

        if tx_ref:
            try:
                order_id = tx_ref.split('_')[1]
                order = Order.objects.get(id=order_id)
            except (Order.DoesNotExist, IndexError, ValueError):
                return render(request, 'main/payment/payment_error.html', {
                    'error': 'Invalid order reference'
                })

            # Save transaction info regardless of status
            order.transaction_ref = tx_ref
            order.flutterwave_transaction_id = transaction_id
            order.payment_method = payment_type or "Flutterwave"
            order.save()

            if status == 'completed' and transaction_id:
                # Verify the payment
                if verify_flutterwave_payment(transaction_id):
                    order.status = 'paid'
                    order.save()
                    total = order.get_total_amount()
                    return render(request, 'main/payment/payment_success.html', {
                        'order': order,
                        'transaction_id': transaction_id,
                        'total': total,
                    })
                else:
                    order.status = 'cancelled'
                    order.save()
                    return render(request, 'main/payment/payment_error.html', {
                        'error': 'Payment verification failed. Your order has been cancelled.'
                    })
            else:
                order.status = 'cancelled'
                order.save()
                return render(request, 'main/payment/payment_error.html', {
                    'error': 'Payment was not successful. Your order has been cancelled.'
                })

    return render(request, 'main/payment/payment_error.html', {
        'error': 'Invalid request method'
    })


def verify_flutterwave_payment(transaction_id):
    """Verify payment with Flutterwave"""
    
    FLUTTERWAVE_SECRET_KEY = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
    
    if not FLUTTERWAVE_SECRET_KEY:
        return False
    
    headers = {
        'Authorization': f'Bearer {FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return (result.get('status') == 'success' and 
                   result.get('data', {}).get('status') == 'successful')
        
        return False
        
    except requests.exceptions.RequestException:
        return False



@csrf_exempt
def payment_webhook(request):
    """Handle webhook notifications from Flutterwave"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Verify webhook signature (recommended for production)
            # You can implement webhook signature verification here
            
            if data.get('event') == 'charge.completed':
                transaction_data = data.get('data', {})
                tx_ref = transaction_data.get('tx_ref')
                status = transaction_data.get('status')
                
                if status == 'successful' and tx_ref:
                    try:
                        order_id = tx_ref.split('_')[1]
                        order = Order.objects.get(id=order_id)
                        
                        if order.status == 'pending':
                            order.status = 'paid'
                            order.save()
                            
                            # You can add additional logic here like sending confirmation emails
                            
                    except (Order.DoesNotExist, IndexError, ValueError):
                        pass
            
            return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error'}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)