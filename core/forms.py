# core/forms.py
from django import forms
from .models import Ad, User
from .models import UserProfile, BusinessProfile, NotificationPreference
from django.contrib.auth.forms import PasswordChangeForm


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



class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            'business_name',
            'business_type',
            'website',
            'gst_number',
            'description',
            'logo'
        ]



class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'})
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            "new_inquiries", 
            "listing_performance", 
            "payment_confirmations", 
            "marketing_updates",
            "urgent_inquiries", 
            "security_alerts",
            "real_time_chat",
            "call_requests"
        ]
        widgets = {
            field: forms.CheckboxInput(attrs={"class": "form-check-input"})
            for field in fields
        }

class VerificationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['govt_id', 'business_license']
        widgets = {
            'govt_id': forms.ClearableFileInput(attrs={'class': 'd-none', 'id': 'govt-id-input'}),
            'business_license': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
