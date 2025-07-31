from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit-picture/', views.edit_profile_picture, name='edit_profile_picture'),
    path('post-ad/', views.select_category, name='select_category'),
    path('post-ad/<slug:category_slug>/', views.post_ad, name='post_ad'),
    path('dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('upgrade-to-seller/', views.upgrade_to_seller, name= 'upgrade_to_seller'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search_results, name='search_results'),

    # Password reset flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'
    ), name='password_reset_complete'),


]
