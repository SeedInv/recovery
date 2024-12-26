from django.urls import path
from . import views

urlpatterns = [
    path('account-statement/', views.account_statement, name='account_statement'),
    path('deposit/', views.deposit, name='deposit'),
    path('create-investment/', views.create_investment, name='create_investment'),
    path('withdrawal-request/', views.withdrawal_request, name='withdrawal_request'),
    path('update-roi/', views.update_roi, name='update_roi'),
]
