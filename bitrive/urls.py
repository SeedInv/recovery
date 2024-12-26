from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('starter-page/', views.get_started, name='get_started'),
    path('funds_recovery/', views.funds_recovery, name='funds_recovery'),
    path('about/', views.about, name='about'),  
    path('services/', views.services, name='services'),  
    path('investment/', views.investment, name='investment'), 
    path('contact/', views.contact, name='contact'), 
    path('team/', views.team, name='team'), 
     
]
