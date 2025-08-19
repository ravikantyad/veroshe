# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, SecurityActivity
from django.contrib.auth.signals import user_logged_in, user_logged_out

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    SecurityActivity.objects.create(
        user=user,
        action='login',
        ip_address=get_client_ip(request),
        browser_info=request.META.get('HTTP_USER_AGENT', '')
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    SecurityActivity.objects.create(
        user=user,
        action='logout',
        ip_address=get_client_ip(request),
        browser_info=request.META.get('HTTP_USER_AGENT', '')
    )