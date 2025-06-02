from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Alert, Stock, Order

User = get_user_model()

@receiver(post_save, sender=Stock)
def check_low_stock(sender, instance, **kwargs):
    if instance.quantity < instance.alert_threshold:
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Alert.objects.create(
                user=admin,
                alert_type='low_stock',
                message=f"Low stock alert: {instance.product.name} has only {instance.quantity} units left (threshold: {instance.alert_threshold})",
                related_object_id=instance.id,
                related_content_type='stock'
            )

@receiver(post_save, sender=Order)
def notify_order_completion(sender, instance, **kwargs):
    if instance.status == 'Completed':
        Alert.objects.create(
            user=instance.buyer.user,
            alert_type='order_completed',
            message=f"Your order #{instance.id} has been completed",
            related_object_id=instance.id,
            related_content_type='order'
        )