from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import User
from .models import Profile
from django.utils.html import format_html
from django.utils.html import mark_safe
from .models import Ad, CATEGORY_CHOICES, favorite
from .models import Category

admin.site.register(Category)

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # You can customize what fields appear here
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email' , 'user_type', 'is_staff')
    
# Register your models here.



class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'profile_image_tag']
    readonly_fields = ['profile_image_tag']

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return mark_safe('<img src="{obj.profile_image.url}" width="40" height="40" style="border-radius:50%;" />')
        return "No image"
    
    profile_image_tag.short_description = 'Profile Picture'

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Ad)
admin.site.register(favorite)
