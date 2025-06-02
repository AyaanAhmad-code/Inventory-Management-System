from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory.models import Stock
from .utils.alerts import check_low_stock_and_alert

from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a Profile when a User is saved.
    """
    if created:
        Profile.objects.create(user=instance)
        print('Profile created!')
    else:
        instance.profile.save()
        print('Profile updated!')



@receiver(post_save, sender=Stock)
def check_stock_level(sender, instance, **kwargs):
    threshold = 10  # You can make this configurable
    if instance.quantity < threshold:
        check_low_stock_and_alert(threshold)