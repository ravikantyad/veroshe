from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Ad, CATEGORY_CHOICES, Favorite, SellerActivity
from django.contrib.auth import logout as auth_logout
from .forms import AdForm, UserForm, UserProfileForm
from .models import UserProfile, Category
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import datetime
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.urls import reverse



User = get_user_model()



def home(request):
    makes = Ad.objects.values_list('make', flat=True).distinct()
    models = Ad.objects.values_list('model', flat=True).distinct()
    submodels = Ad.objects.values_list('sub_model', flat=True).distinct()
    ads = Ad.objects.filter(is_active=True, is_expired=False).order_by('-created_at') # assuming you want latest first
    categories = Category.objects.all()
    years = list(range(datetime.now().year, 1950, -1))
     
    # Define makes, models, and submodels as empty lists or fetch them as needeed

    return render(request, 'core/home.html', {
        'categories': categories,
        'ads': ads,
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
                link=reverse('ad_detail', kwargs={'pk': ad.pk})
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



def buyer_dashboard(request):
    return render(request, 'core/buyer_dashboard.html')


def upgrade_to_seller(request):
    user = request.user
    user.user_type ='seller'
    user.save()
    return redirect('seller_dashboard')

@login_required
def search_results(request):
    make = request.GET.get('make')
    model = request.GET.get('model')
    submodel = request.GET.get('submodel')
    location = request.GET.get('location')
    category = request.GET.get('category')
    year = request.GET.get('year')
    query = request.GET.get('q')

    ads = Ad.objects.all()
    
    if make:
        ads = ads.filter(make__iexact=make)
    if model:
        ads = ads.filter(model__iexact=model)
    if submodel:
        ads = ads.filter(sub_model__icontains=submodel)
    if location:
        ads = ads.filter(location__icontains=location)
    if category:
        ads = ads.filter(category__name__iexact=category)
    if year:
        ads = ads.filter(year=year)
    if query:
        ads = ads.filter(title__icontains=query)

    return render(request, 'core/search_results.html', {'ads': ads})

# views.py

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
        'profile_form': profile_form
    })