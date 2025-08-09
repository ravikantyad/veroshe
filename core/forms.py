# core/forms.py
from django import forms
from .models import Ad, User
from .models import UserProfile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'full_name', 'email', 'phone_number', 'street_name', 'city', 'state', 'pincode', 'country']


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = [
            'title', 'make', 'model', 'sub_model', 'year',
            'fuel_type', 'transmission', 'price', 'location',
            'mobile_number', 'description', 'image'
        ]
