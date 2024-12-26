# userprofile/urls.py
from django.urls import path
from . import views  # Import the views
from django.contrib.auth import views as auth_views




urlpatterns = [
    path('register/', views.register_view, name='register'),  # URL for registration
    path('login/', views.login_view, name='login'),  # URL for login
    path('profile/', views.profile_view, name='profile'),  # URL for profile
    path('logout/', views.logout_view, name='logout'),  # URL for logout
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),
   

]
