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
from .models import Ad, favorite, CATEGORY_CHOICES
from django.contrib.auth import logout as auth_logout
from .forms import AdForm
from .models import Profile, Category
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import datetime


User = get_user_model()



def home(request):
    makes = Ad.objects.values_list('make', flat=True).distinct()
    models = Ad.objects.values_list('model', flat=True).distinct()
    submodels = Ad.objects.values_list('sub_model', flat=True).distinct()
    ads = Ad.objects.all().order_by('-created_at') # assuming you want latest first
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


def seller_dashboard(request):
    user = request.user

    posted_ads_count = Ad.objects.filter(seller=user).count()
    favourite_ads_count = favorite.objects.filter(user=user).count()
    expired_ads_count = Ad.objects.filter(seller=user, is_expired=True).count()

    # Recent ads
    seller_ads = Ad.objects.filter(seller=user).order_by('-created_at')

    recent_ads = seller_ads[:3]

    # Ads view data for chart
    ads_views_data = Ad.objects.filter(seller=user).values_list('views', flat=True)[:7]
    ads_views = list(ads_views_data) + [0] * (7 - len(ads_views_data))
    if not any(ads_views):
        ads_views = [0,0,0,0,0,0,0]  # pad to 7 items

    print("ads_views data:", ads_views)

    # Recent activities placeholder (replace with real logs if you have them)
    recent_activities = [
        {'message': 'Your ad "v21 48mp ois selfie" is successfully published.', 'link': '#'},
        {'message': 'John Wick saved your ad to his favourites.', 'link': '#'},
        {'message': 'Please complete your profile editing to post ads.', 'link': None},
        {'message': 'Your ad "converse blue training shoes" is published.', 'link': '#'},
        {'message': '5 days remaining to complete membership payment.', 'link': '#'},
    ]

    context = {
        'posted_ads_count': posted_ads_count,
        'favourite_ads_count': favourite_ads_count,
        'expired_ads_count': expired_ads_count,
        'recent_ads': recent_ads,
        'ads_views': ads_views,
        'recent_activities': recent_activities,
    }

    return render(request, 'core/seller_dashboard.html', context)

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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def edit_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        profile.phone_number = request.POST.get('phone')
        user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('edit_profile')

    return render(request, 'core/edit_profile.html', {'profile': profile})

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



