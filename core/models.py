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

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/profile-l.png', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
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
    category = models.ForeignKey(Category, on_delete= models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    make = models.CharField(max_length=255, default='Unknown', blank=True)
    model = models.CharField(max_length=255, default='Unknown', blank=True )
    sub_model = models.CharField(max_length=100,blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='Unknown', blank=True)
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





class favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    
    def __str__(self):
        return self.user.username
    


