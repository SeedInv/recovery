# connectwallet/urls.py
from django.urls import path
from . import views

urlpatterns = [
     path('select-wallet/', views.select_wallet, name='select_wallet'),
]
