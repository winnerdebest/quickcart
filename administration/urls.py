from django.urls import path
from . import views



urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('products/create/', views.product_create_update, name='product_create'),
    path('products/edit/<int:pk>/', views.product_create_update, name='product_edit'),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
]
