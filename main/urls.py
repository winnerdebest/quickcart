from django.urls import path
from .views import *


urlpatterns = [
    path('', products, name='products'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('checkout/', checkout_view, name='checkout'),
    path('checkout/process/', process_checkout, name='process_checkout'),
    path('payment/callback/', payment_callback, name='payment_callback'),
    path('payment/webhook/', payment_webhook, name='payment_webhook'),
]
