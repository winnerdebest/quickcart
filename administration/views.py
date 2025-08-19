from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from main.models import Product, Order  # Import Product model
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.auth.decorators import login_required



@login_required
def admin_dashboard(request):
    query = request.GET.get('q', '')
    product_list = Product.objects.all()
    if query:
        product_list = product_list.filter(name__icontains=query)
    paginator = Paginator(product_list, 8)  # 8 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
    })
    
    
@login_required
def product_create_update(request, pk=None):
    if pk:  # Editing
        product = get_object_or_404(Product, pk=pk)
    else:   # Creating
        product = None

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        if product:  # update
            product.name = name
            product.description = description
            product.price = price
            if image:
                product.image = image
            product.save()
        else:  # create
            product = Product.objects.create(
                name=name,
                slug=slugify(name),
                description=description,
                price=price,
                image=image,
            )
        return redirect("product_detail", slug=product.slug)

    return render(request, "product_form.html", {"product": product})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("admin_dashboard") 


@login_required
def order_list(request):
    query = request.GET.get("q", "")   # search query
    orders = Order.objects.all()

    if query:
        orders = orders.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(status__icontains=query)
        )

    # Pagination
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Stats
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="pending").count()
    paid_orders = Order.objects.filter(status="paid").count()
    completed_orders = Order.objects.filter(status="completed").count()
    shipped_orders = Order.objects.filter(status="shipped").count()
    cancelled_orders = Order.objects.filter(status="cancelled").count()

    context = {
        "orders": page_obj,   # paginated queryset
        "query": query,       # to keep search term in template
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "shipped_orders": shipped_orders,
        "cancelled_orders": cancelled_orders,
        "paid_orders": paid_orders,
    }
    return render(request, "orders/order_list.html", context)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        if order.status == "paid":  # only allow shipping if already paid
            order.status = "shipped"
            order.save()
        return redirect("order_detail", pk=order.pk)

    return render(request, "orders/order_detail.html", {"order": order})