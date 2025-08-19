from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock_display", "created_at", "updated_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")

    def stock_display(self, obj):
        # Show stock if field exists, else "N/A"
        return getattr(obj, "stock", "N/A")
    stock_display.short_description = "Stock"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "get_total_price")
    can_delete = False

    def get_total_price(self, obj):
        if obj.price is None or obj.quantity is None:
            return 0
        return obj.get_total_price()
    get_total_price.short_description = "Total Price"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "phone", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "phone", "address")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at",)
