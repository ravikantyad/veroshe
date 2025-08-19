from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User




class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )
    user_type = models.CharField(max_length= 10, choices=USER_TYPE_CHOICES, default='buyer')
    profile_image = models.ImageField(upload_to='profiles/', blank= True, null=True)

CATEGORY_CHOICES = [
    ('engine', 'Engine Parts'),
    ('lights', 'Lights & Electricals'),
    ('body', 'Body Parts'),
    ('interior', 'Interiors'),
    ('wheels', 'Wheels & Tyres'),
    ('brakes', 'Brakes'),
    ('suspension', 'Suspension'),
    ('exhaust', 'Exhaust'),
    ('transmission', 'Transmission'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    
    profile_picture = models.ImageField(upload_to='profile_images/', default='profile_images/profile-l.png', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    phone_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)

    govt_id = models.FileField(upload_to='verification/govt_ids/', blank=True, null=True)
    govt_id_verified = models.BooleanField(default=False)

    business_license = models.FileField(upload_to='verification/business_licenses/', blank=True, null=True)
    business_license_verified = models.BooleanField(default=False)

    # Address Fields
    street_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)


    def __str__(self):
        return self.user.username
    

class BusinessProfile(models.Model):
    BUSINESS_TYPES = [
        ('retail', 'Retail'),
        ('service', 'Service'),
        ('manufacturing', 'Manufacturing'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPES, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)

    def __str__(self):
        return self.business_name or f"{self.user.username}'s Business"
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

FUEL_CHOICES = [
    ('petrol', 'Petrol'),
    ('diesel', 'Diesel'),
    ('electric', 'Electric'),
    ('hybrid', 'Hybrid'),
]

TRANSMISSION_CHOICES = [
    ('Automatic', 'Automatic'),
    ('Manual', 'Manual'),
]

class Ad(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, choices=CATEGORY_CHOICES, on_delete= models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    sub_model = models.CharField(max_length=100, null=True, blank=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, null=True, blank=True)
    transmission = models.CharField(max_length=20,choices=TRANSMISSION_CHOICES, default='Manual', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title




class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    ad = models.ForeignKey('Ad', on_delete=models.CASCADE, related_name='favorited_by')
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ad')  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} favorited {self.ad.title}"
    

class SellerActivity(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.username} - {self.message}"


class SecurityActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="security_activities")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser_info = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} at {self.timestamp}"
    
class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Email Notifications
    new_inquiries = models.BooleanField(default=True)
    listing_performance = models.BooleanField(default=True)
    payment_confirmations = models.BooleanField(default=True)
    marketing_updates = models.BooleanField(default=False)

    # SMS Notifications
    urgent_inquiries = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)

    # Push Notifications
    real_time_chat = models.BooleanField(default=True)
    call_requests = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Preferences"

