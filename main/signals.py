from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .utils.notifications import send_notify_event

@receiver(post_save, sender=Order)
def order_notifications(sender, instance, created, **kwargs):
    """
    Send a notification only when an order is marked as paid.
    Works for:
      - New order created with status 'paid'
      - Existing order updated from another status to 'paid'
    """
    # Only trigger if status is 'paid'
    if instance.status != "paid":
        return

    # Optional: avoid sending multiple notifications if already sent
    if getattr(instance, "_notify_paid_sent", False):
        return

    # Send the notification
    send_notify_event(
        f"✅ Order Paid!\nOrder ID: {instance.id}\nCustomer: {instance.full_name}\nTotal: {instance.get_total_amount()}",
        "Order Paid"
    )

    # Mark this instance so multiple saves in same request/session don’t resend
    instance._notify_paid_sent = True
