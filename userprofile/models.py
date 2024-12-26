# userprofile/models.py
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    country = CountryField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    
    def __str__(self):
        return f"User: {self.user.username}, Email: {self.user.email}, Phone: {self.phone_number}, " \
               f"Wallet: {self.wallet_address}, Country: {self.country}, Address: {self.address}, " \
               f"Balance: {self.balance}"