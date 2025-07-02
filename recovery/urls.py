# urls.py
from django.urls import path
from . import views

app_name = 'recovery'

urlpatterns = [
    path('form/', views.recovery_form, name='form'),
    path('success/', views.success, name='success'),
]
