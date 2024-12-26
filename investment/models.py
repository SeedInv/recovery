from django.db import models
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from decimal import Decimal
from django.core.mail import send_mail
import time
from django.utils import timezone
from datetime import timedelta
from django.apps import apps

# Define the Plan model first
class Plan(models.Model):
    name = models.CharField(max_length=255)  # Name of the plan (e.g., Basic, Premium)
    duration_days = models.IntegerField()  # Duration of the plan in days
    roi_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Return on investment rate (e.g., 10.00 for 10%)

    def __str__(self):
        return f"{self.name} ({self.duration_days} days, {self.roi_rate}% ROI)"


# Transaction model
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('roi', 'Return on Investment'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of ${self.amount} by {self.user.username}"

    def approve(self):
        if self.status == 'pending':
            self.status = 'approved'
            self.save()
            send_mail(
                subject="Transaction Approved",
                message=f"Your {self.transaction_type} of ${self.amount} has been approved.",
                from_email="no-reply@yourdomain.com",
                recipient_list=[self.user.email],
            )


class Investment(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    roi_accumulated = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    deposit_time = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Investment of ${self.deposit_amount} by {self.user_profile.user.username}"

    def save(self, *args, **kwargs):
        # Ensure deposit_time is not None (auto_now_add=True should handle this)
        if self.deposit_time is None:
            self.deposit_time = timezone.now()

        # Check if end_date is already set; if not, calculate it
        if not self.end_date and self.deposit_time and self.plan:
            # Calculate the end date based on the deposit_time and plan duration
            self.end_date = self.deposit_time + timedelta(days=self.plan.duration_days)

        # Print for debugging
        print("Saving Investment:", self.deposit_time, self.end_date)

        # Save the investment object
        super().save(*args, **kwargs)

    def calculate_roi(self):
        # Check if the investment has expired, stop calculating ROI if expired
        if self.end_date and timezone.now() >= self.end_date:
            self.is_active = False  # Mark the investment as inactive
            self.save()  # Save the updated status
            return self.roi_accumulated  # No further ROI should be calculated

        # If still active, calculate ROI
        time_elapsed = timezone.now() - self.deposit_time
        days_elapsed = time_elapsed.days  # Get the number of days

        roi_rate = self.plan.roi_rate
        roi_per_day = self.deposit_amount * (roi_rate / Decimal('100')) / Decimal('365')  # Daily ROI

        return roi_per_day * days_elapsed  # Return the accumulated ROI

    def update_roi(self):
        # Update the accumulated ROI
        new_roi = self.calculate_roi()
        self.roi_accumulated = new_roi
        self.last_updated = timezone.now()  # Use Django's timezone to record the update time
        self.save()

    def is_expired(self):
        # Utility method to check if the investment is expired
        return self.end_date and timezone.now() >= self.end_date

    def activate_investment(self):
        # Activate investment by increasing the deposit (e.g., multiplying by 5)
        self.deposit_amount *= 5
        self.save()

# WithdrawalRequest model
class WithdrawalRequest(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def approve(self):
        if self.user_profile.balance >= self.amount:
            self.user_profile.balance -= self.amount
            self.user_profile.save()
            self.approved = True
            self.save()

            Transaction.objects.create(
                user=self.user_profile.user,
                amount=self.amount,
                transaction_type='withdrawal',
                status='approved',
                description="Approved withdrawal"
            )

            send_mail(
                subject="Withdrawal Approved",
                message=f"Your withdrawal of ${self.amount} has been approved.",
                from_email="no-reply@yourdomain.com",
                recipient_list=[self.user_profile.user.email],
            )
        else:
            raise ValueError("Insufficient balance to approve this withdrawal")

    def __str__(self):
        return f"Withdrawal request by {self.user_profile.user.username} for ${self.amount}"
