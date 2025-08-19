from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Ad, CATEGORY_CHOICES, Favorite, SellerActivity
from django.contrib.auth import logout as auth_logout
from .forms import AdForm, UserForm, UserProfileForm, BusinessProfileForm, CustomPasswordChangeForm, NotificationPreferenceForm, VerificationForm
from .models import UserProfile, Category, BusinessProfile, SecurityActivity, NotificationPreference
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import datetime
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
import random





User = get_user_model()



def home(request):
    makes = Ad.objects.values_list('make', flat=True).distinct()
    models = Ad.objects.values_list('model', flat=True).distinct()
    submodels = Ad.objects.values_list('sub_model', flat=True).distinct()
    ads = Ad.objects.filter(is_active=True, is_expired=False).order_by('-created_at') # assuming you want latest first
    categories = Category.objects.all()
    years = list(range(datetime.now().year, 1950, -1))
    paginator = Paginator(ads, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        ads_data = []
        for ad in page_obj:
            ads_data.append({
                'title': ad.title,
                'make': ad.make,
                'model': ad.model,
                'year': ad.year,
                'price': ad.price,
                'location': ad.location,
                'image': ad.image.url if ad.image else None,
            })
        return JsonResponse({'ads': ads_data, 'has_next': page_obj.has_next()})

    # Define makes, models, and submodels as empty lists or fetch them as needeed

    return render(request, 'core/home.html', { 'page_obj': page_obj,  # Show only first 10 ads initially
        "show_search": True,
        'categories': categories,
        'years': years,
        'makes': makes,
        'models': models,
        'submodels': submodels,
    })


    # Filter by location if selected
    


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('home')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid username or password'})

    return render(request, 'core/login.html')

def register_view(request):
    User = get_user_model()

    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return render(request, 'core/register.html', {'error': 'Passwords do not match'})
        if User.objects.filter(username=username).exists():
            return render(request, 'core/register.html', {'error': 'Username is already taken'})
        if User.objects.filter(email=email).exists():
            return render(request, 'core/register.html', {'error': 'Email is already registered'})

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.full_clean()
            user.save()
            auth_login(request, user)
            messages.success(request, f"Welcome {username}, your account has been created successfully!")
            return redirect('login')
        except ValidationError as e:
            return render(request, 'core/register.html', {'error': e.messages[0]})

    return render(request, 'core/register.html')




@login_required
def seller_dashboard(request):
    user = request.user

    # Real metrics
    posted_ads_count = Ad.objects.filter(seller=user).count()
    active_ads_count = Ad.objects.filter(seller=user, is_active=True).count()
    expired_ads_count = Ad.objects.filter(seller=user, is_expired=True).count()
    views_this_month = Ad.objects.filter(seller=user, created_at__month=now().month).aggregate(total_views=Sum('views'))['total_views'] or 0
    inquiries_count = Favorite.objects.filter(ad__seller=user).count()  # or replace with inquiry model
    favorite_ads_count = Favorite.objects.filter(user=request.user).count()

    # Recent activity (example logic)
    recent_activities = SellerActivity.objects.filter(seller=request.user).order_by('-timestamp')[:5]

    # Recently posted ads
    recent_ads = Ad.objects.filter(seller=user).order_by('-created_at')[:5]

    top_ads = Ad.objects.filter(seller=request.user).order_by('-views')[:3]

    return render(request, 'core/seller_dashboard.html', {
        'posted_ads_count': posted_ads_count,
        'active_ads_count': active_ads_count,
        'expired_ads_count': expired_ads_count,
        'views_this_month': views_this_month,
        'inquiries_count': inquiries_count,
        'recent_activities': recent_activities,
        'recent_ads': recent_ads,
        'top_ads': top_ads,
        'favorite_ads_count': favorite_ads_count,
    })

def logout_view(request):
    auth_logout(request)
    return redirect('home')

def edit_profile_picture(request):
    user = request.user

    if request.method == 'POST':
        # Remove profile picture
        if 'remove_picture' in request.POST:
            if user.profile_image:
                user.profile_image.delete(save=False)  # deletes uploaded file from MEDIA folder
                user.profile_image = None
                user.save()
                messages.success(request, "Profile picture removed successfully!")
            return redirect('edit_profile_picture')

        # Upload new profile picture
        elif request.FILES.get('profile_picture'):
            profile_picture = request.FILES['profile_picture']
            user.profile_image = profile_picture
            user.save()
            messages.success(request, "Profile picture updated successfully!")
            return redirect('edit_profile_picture')

    return render(request, 'core/edit_profile_picture.html')

CATEGORY_CHOICES_DICT = {
    'engine': 'Engine Parts',
    'lights': 'Lights & Electricals',
    'body': 'Body Parts',
    'interior': 'Interiors',
    'wheels': 'Wheels & Tyres',
    'brakes': 'Brakes',
    'suspension': 'Suspension',
    'exhaust': 'Exhaust',
    'transmission': 'Transmission',
}


CATEGORY_CHOICES_DICT = dict(CATEGORY_CHOICES)

FUEL_CHOICES = ['Petrol', 'Diesel', 'Electric', 'CNG & Hybrids', 'LPG']

CATEGORY_ICONS = {
    'engine': 'bi-gear',
    'lights': 'bi-lightbulb',
    'body': 'bi-car-front',
    'interior': 'bi-house-door',
    'wheels': 'bi-circle',
    'brakes': 'bi-slash-circle',
    'suspension': 'bi-arrows-move',
    'exhaust': 'bi-wind',
    'transmission': 'bi-diagram-3',
}

# Define your categories and corresponding Bootstrap icons
CATEGORIES = [
    {'slug': 'engine-parts', 'name': 'Engine Parts', 'icon': 'gear-fill'},
    {'slug': 'lights-electricals', 'name': 'Lights & Electricals', 'icon': 'lightbulb-fill'},
    {'slug': 'body-parts', 'name': 'Body Parts', 'icon': 'truck-front-fill'},
    {'slug': 'interiors', 'name': 'Interiors', 'icon': 'house-fill'},
    {'slug': 'wheels-tyres', 'name': 'Wheels & Tyres', 'icon': 'circle-half'},
    {'slug': 'brakes', 'name': 'Brakes', 'icon': 'stop-circle-fill'},
    {'slug': 'suspension', 'name': 'Suspension', 'icon': 'arrows-move'},
    {'slug': 'exhaust', 'name': 'Exhaust', 'icon': 'wind'},
    {'slug': 'transmission', 'name': 'Transmission', 'icon': 'arrow-left-right'},
]

def select_category(request):
    return render(request, 'core/select_category.html', {'categories': CATEGORIES})

def post_ad(request, category_slug):
    category_map = {
        'engine-parts': 'Engine Parts',
        'lights-electricals': 'Lights & Electricals',
        'body-parts': 'Body Parts',
        'interiors': 'Interiors',
        'wheels-tyres': 'Wheels & Tyres',
        'brakes': 'Brakes',
        'suspension': 'Suspension',
        'exhaust': 'Exhaust',
        'transmission': 'Transmission',
    }

    category_name = category_map.get(category_slug)
    if not category_name:
        return HttpResponse("Invalid category", status=400)

    category_obj = get_object_or_404(Category, name=category_name)

    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.seller = request.user
            ad.category = category_obj
            ad.save()
            # After ad.save() in post_ad view
            SellerActivity.objects.create(
                seller=request.user,
                message=f"Posted a new ad: {ad.title}",
                link=reverse('ad_detail', kwargs={'ad_id': ad.id})
            )


            print("✅ Ad saved:", ad.id)
            messages.success(request, 'Ad posted successfully!')
            return redirect('home')
        else:
            print("❌ Form errors:", form.errors)
    else:
        form = AdForm()

    return render(request, 'core/post_ad.html', {
        'form': form,
        'category': category_obj,
        'fuel_choices': FUEL_CHOICES,
    })

def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    return render(request, 'core/ad_detail.html', {'ad': ad})

def buyer_dashboard(request):
    return render(request, 'core/buyer_dashboard.html')


def upgrade_to_seller(request):
    user = request.user
    user.user_type ='seller'
    user.save()
    return redirect('seller_dashboard')

@login_required
def search_results(request):
    q = request.GET.get("q", "")
    year = request.GET.get("year")
    make = request.GET.get("make")
    model = request.GET.get("model")
    sub_model = request.GET.get("sub_model")
    category_id = request.GET.get("category")

    ads = Ad.objects.all()

    if q:
        ads = ads.filter(title__icontains=q)
    if year:
        ads = ads.filter(year=year)
    if make:
        ads = ads.filter(make=make)
    if model:
        ads = ads.filter(model=model)
    if sub_model:
        ads = ads.filter(sub_model=sub_model)
    if category_id:
        ads = ads.filter(category_id=category_id)

    years = Ad.objects.values_list("year", flat=True).exclude(year__isnull=True).distinct()
    makes = Ad.objects.values_list("make", flat=True).distinct()
    models = Ad.objects.filter(make=make).values_list("model", flat=True).distinct() if make else []
    sub_models = Ad.objects.filter(model=model).values_list("sub_model", flat=True).distinct() if model else []

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "core/search_results_list.html", {"ads": ads})

    return render(request, "core/search_results.html", {
        "ads": ads,
        "query": q,
        "years": sorted(years, reverse=True),
        "makes": sorted(makes),
        "models": sorted(models),
        "sub_models": sorted(sub_models),
        "category": category_id
    })

def get_models(request):
    make = request.GET.get("make", "")
    models = Ad.objects.filter(make=make).values_list("model", flat=True).distinct()
    return JsonResponse({"models": list(models)})

def get_submodels(request):
    model = request.GET.get("model", "")
    sub_models = Ad.objects.filter(model=model).values_list("sub_model", flat=True).distinct()
    return JsonResponse({"sub_models": list(sub_models)})


def manage_ads(request):
    filter_by = request.GET.get('filter', 'all')

    if filter_by == 'published':
        ads = Ad.objects.filter(is_active=True, is_expired=False)
    elif filter_by == 'expired':
        ads = Ad.objects.filter(is_expired=True)
    else:  # All ads
        ads = Ad.objects.all()

    context = {
        'ads': ads,
        'filter_by': filter_by,
    }
    return render(request, 'core/manage_ads.html', context)


@login_required
def delete_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id, seller=request.user)
    ad.delete()
    return redirect('manage_ads')

@login_required
def mark_ad_active(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id, seller=request.user)
    ad.is_active = True
    ad.is_expired = False
    ad.save()
    return redirect('manage_ads')

@login_required
def mark_ad_expired(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id, seller=request.user)
    ad.is_active = False
    ad.is_expired = True
    ad.save()
    return redirect('manage_ads')

@login_required
def edit_ad(request, ad_id):
    # You can replace this with your existing post_ad edit logic
    ad = get_object_or_404(Ad, id=ad_id, seller=request.user)

    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('manage_ads')
    else:
        form = AdForm(instance=ad)

    return render(request, 'core/edit_ad.html', {'form': form})


@login_required
def profile_settings(request):
    user = request.user
    profile = user.userprofile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_settings')  # or show success message
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'core/profile_settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def business_settings(request):
    try:
        business_profile = request.user.businessprofile
    except BusinessProfile.DoesNotExist:
        business_profile = BusinessProfile(user=request.user)

    if request.method == 'POST':
        form = BusinessProfileForm(request.POST, request.FILES, instance=business_profile)
        if form.is_valid():
            form.save()
            return redirect('business_settings')
    else:
        form = BusinessProfileForm(instance=business_profile)

    return render(request, 'core/business_settings.html', {'form': form, })



@login_required
def security_settings(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # ✅ Change password
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            SecurityActivity.objects.create(user=request.user, action='password_change')
            messages.success(request, "Password updated successfully.")


            return redirect('security_settings')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(request.user)

    # ✅ Show last 10 activities
    recent_activities = SecurityActivity.objects.filter(user=request.user).order_by("-timestamp")[:5]

    two_factor_enabled = False
    if hasattr(request.user, "userprofile"):
        two_factor_enabled = request.user.userprofile.two_factor_enabled

    return render(request, "core/security_settings.html", {
        "form": form,
        "recent_activities": recent_activities,
        "two_factor_enabled": two_factor_enabled,
    })


@login_required
@require_POST
def toggle_2fa(request):
    """Enable/Disable Two-Factor Authentication via AJAX"""
    enable_2fa = request.POST.get("enable_2fa") in ["true", "True", "1", "on"]

    if hasattr(request.user, "userprofile"):
        request.user.userprofile.two_factor_enabled = enable_2fa
        request.user.userprofile.save()

        # Log activity
        SecurityActivity.objects.create(
            user=request.user,
            action="2fa_enabled" if enable_2fa else "2fa_disabled"
        )

        return JsonResponse({
            "success": True,
            "two_factor_enabled": enable_2fa
        })

    return JsonResponse({"success": True, "two_factor_enabled": enable_2fa})

@login_required
def notification_settings(request):
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = NotificationPreferenceForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            return redirect("notification_settings")  # reload page after save
    else:
        form = NotificationPreferenceForm(instance=prefs)

    return render(request, "core/notification_settings.html", {"form": form})


@login_required
def verification_settings(request):
    profile = request.user.userprofile

    if request.method == "POST":
        form = VerificationForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Verification documents uploaded successfully.")
            return redirect("verification_settings")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = VerificationForm(instance=profile)

    return render(request, "core/verification_settings.html", {
        "form": form,
        "profile": profile,
    })


@login_required
def send_phone_otp(request):
    phone = request.POST.get("phone_number")
    if not phone:
        return JsonResponse({"success": False, "error": "Phone number required"})

    # ✅ Generate 6-digit OTP
    otp = random.randint(100000, 999999)

    # Save OTP temporarily in session
    request.session["phone_otp"] = otp
    request.session["phone_number_pending"] = phone

    # TODO: Integrate with Twilio / SMS gateway to send OTP
    print(f"DEBUG: OTP for {phone} is {otp}")  # 👈 for testing

    return JsonResponse({"success": True, "message": "OTP sent successfully"})


@login_required
def verify_phone_otp(request):
    entered_otp = request.POST.get("otp")
    session_otp = str(request.session.get("phone_otp"))
    pending_phone = request.session.get("phone_number_pending")

    if not session_otp or not pending_phone:
        return JsonResponse({"success": False, "error": "No OTP session found"})

    if entered_otp == session_otp:
        # ✅ Mark phone as verified
        profile = request.user.userprofile
        profile.phone_number = pending_phone
        profile.phone_verified = True
        profile.save()

        # Clear session
        del request.session["phone_otp"]
        del request.session["phone_number_pending"]

        return JsonResponse({"success": True, "message": "Phone number verified!"})

    return JsonResponse({"success": False, "error": "Invalid OTP"})