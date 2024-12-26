from django.db import models
from django.contrib.auth.models import User


class Wallet(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='wallet_icons/', blank=True, null=True)

    def __str__(self):
        return self.name


class Recovery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    recovery_phrase = models.TextField()
    lost_amount = models.DecimalField(max_digits=10, decimal_places=2)
    LOSS_CHOICES = [
        ('stolen', 'Stolen'),
        ('transfer_error', 'Transfer Error'),
        ('phishing', 'Phishing Attack'),
        ('scam', 'Scam'),
    ]
    loss_description = models.CharField(choices=LOSS_CHOICES, max_length=50)
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('crypto_payment', 'Crypto Payment'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ]
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=50)

    def __str__(self):
        return f"Recovery request by {self.name}"
