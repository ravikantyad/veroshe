# core/forms.py
from django import forms
from .models import Ad, User


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = [
            'title', 'vehicle_name', 'model', 'sub_model', 'year',
            'fuel_type', 'transmission', 'price', 'location',
            'mobile_number', 'description', 'image'
        ]
