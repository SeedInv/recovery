from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Investment, Transaction, WithdrawalRequest
from userprofile.models import UserProfile
from decimal import Decimal
from django.contrib import messages
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.utils import timezone
from .models import Investment, Transaction, Plan
import logging
from django.utils.timezone import now as timezone_now  # Alias 'now' as 'timezone_now'
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .tasks import update_user_roi
from django.core.mail import send_mail
from django.conf import settings







# @login_required
# def account_statement(request):
#     # Fetch all transactions related to the logged-in user, ordered by date
#     transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

#     # Filter only 'roi' transactions for ROI updates
#     roi_transactions = transactions.filter(transaction_type='roi')

#     # Calculate the total ROI earned by summing the 'amount' of each ROI transaction
#     total_roi = roi_transactions.aggregate(total_roi=Sum('amount'))['total_roi'] or Decimal('0.00')

#     # Get the current balance from the user's profile
#     updated_balance = request.user.userprofile.balance

#     # Prepare context for rendering in the template
#     context = {
#         'transactions': transactions,  # All transactions, including ROI and others
#         'roi_transactions': roi_transactions,  # Only ROI-related transactions
#         'balance': updated_balance,  # Current balance from user profile
#         'total_roi': total_roi,  # Total ROI amount
#     }

#     return render(request, 'investment/account_statement.html', context)



@login_required
def account_statement(request):
    # Fetch all transactions related to the logged-in user, ordered by date
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    # Filter only 'roi' transactions for ROI updates
    roi_transactions = transactions.filter(transaction_type='roi')

    # Calculate the total ROI earned by summing the 'amount' of each ROI transaction
    total_roi = roi_transactions.aggregate(total_roi=Sum('amount'))['total_roi'] or Decimal('0.00')

    # Get the current balance from the user's profile (UserProfile model)
    user_profile = UserProfile.objects.get(user=request.user)  # Fetch the user profile
    updated_balance = user_profile.balance

    # Prepare context for rendering in the template
    context = {
        'transactions': transactions,  # All transactions, including ROI and others
        'roi_transactions': roi_transactions,  # Only ROI-related transactions
        'balance': updated_balance,  # Current balance from user profile
        'total_roi': total_roi,  # Total ROI amount
        'user': request.user,  # Pass the logged-in user to the template
        'user_profile': user_profile,  # Pass the user profile to the template
    }

    return render(request, 'investment/account_statement.html', context)

@login_required
def deposit(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount'))
        except (TypeError, ValueError):
            return redirect('account_statement')

        user_profile = request.user.userprofile

        if amount > 0:
            user_profile.balance += amount
            user_profile.save()

            roi = amount * 5  # Assuming ROI is 5 times the deposit amount

            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='deposit',
                status='approved',
                description="Deposit"
            )

            Transaction.objects.create(
                user=request.user,
                amount=roi,
                transaction_type='roi',
                status='approved',
                description="Return on Investment (ROI)"
            )

            messages.success(request, f"Deposit of ${amount} made successfully!")
        else:
            messages.error(request, "Invalid deposit amount.")
        
        return redirect('account_statement')

    return render(request, 'investment/deposit.html')



@login_required
def withdrawal_request(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount'))
        except (TypeError, ValueError):
            messages.error(request, "Invalid amount entered. Please enter a valid number.")
            return redirect('account_statement')

        user_profile = request.user.userprofile

        if amount <= 0:
            messages.error(request, "Withdrawal amount must be greater than zero.")
            return redirect('account_statement')

        if user_profile.balance >= amount:
            # Create withdrawal request
            WithdrawalRequest.objects.create(user_profile=user_profile, amount=amount)

            # Create a transaction for withdrawal
            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='withdrawal',  # Ensure transaction type is 'withdrawal'
                status='pending',
                description="Withdrawal Request"
            )

            # Deduct from the user's balance
            user_profile.balance -= amount
            user_profile.save()

            messages.success(request, f"Your withdrawal request for ${amount} has been submitted and is pending approval.")
            return redirect('account_statement')
        else:
            messages.error(request, "Insufficient balance for withdrawal.")
            return redirect('account_statement')

    return render(request, 'investment/withdrawal_request.html')




logger = logging.getLogger(__name__)

@login_required
def update_roi(request):
    user_profile = request.user.userprofile

    # Get the default plan for the user or fetch a specific one
    default_plan = Plan.objects.first()  # Adjust this to fetch the correct plan based on your logic
    if not default_plan:
        logger.error("No investment plan available for user: %s", request.user.username)
        return JsonResponse({'status': 'error', 'message': 'No investment plan available. Please contact support.'})

    # Get or create investment
    investment, created = Investment.objects.get_or_create(
        user_profile=user_profile,
        defaults={
            'deposit_amount': Decimal('0.00'),
            'roi_accumulated': Decimal('0.00'),
            'plan': default_plan,
        }
    )

    # Ensure deposit_amount is valid
    if investment.deposit_amount <= 0:
        logger.warning("Invalid deposit amount for user: %s", request.user.username)
        return JsonResponse({'status': 'error', 'message': 'Invalid deposit amount. Please check your investment.'})

    # Calculate ROI increment (e.g., 5% of the deposit amount)
    roi_increment = investment.deposit_amount * Decimal('0.05')
    if roi_increment <= 0:
        logger.warning("ROI increment calculation resulted in 0 or negative for user: %s", request.user.username)
        return JsonResponse({'status': 'error', 'message': 'ROI calculation error. Please contact support.'})

    # Update accumulated ROI
    investment.roi_accumulated += roi_increment
    investment.last_updated = timezone_now()
    investment.save()

    # Record the transaction
    Transaction.objects.create(
        user=request.user,
        transaction_type='roi',
        amount=roi_increment,
        status='approved',
        created_at=timezone_now(),
        description=f"ROI of ${roi_increment} earned from deposit of ${investment.deposit_amount}."
    )

    # Send the email notification to the user
    email_subject = 'Your ROI has been updated!'
    email_message = f'Hello {request.user.username},\n\n' \
                    f'Your ROI has been successfully updated. Your new ROI balance is ${investment.roi_accumulated}.\n\n' \
                    f'Thank you for investing with us!\n' \
                    f'Best regards,\nYour Investment Team'

    send_mail(
        email_subject,
        email_message,
        settings.DEFAULT_FROM_EMAIL,  # Ensure you have configured this in your settings
        [request.user.email],
        fail_silently=False,
    )

    # Add a success message for the user to see on the page
    messages.success(request, f"Your ROI has been successfully updated! Your new ROI balance is ${investment.roi_accumulated}.")

    # Log success and return response
    logger.info("ROI updated successfully for user: %s, New ROI: %s", request.user.username, investment.roi_accumulated)

    return JsonResponse({'status': 'success', 'roi': str(investment.roi_accumulated)})


@login_required
def create_investment(request):
    # Hardcoded 6 predefined investment plans
    plans = [
        {"id": 1, "name": "Basic Plan", "duration_days": 30, "roi_rate": 5.0},
        {"id": 2, "name": "Silver Plan", "duration_days": 60, "roi_rate": 7.0},
        {"id": 3, "name": "Gold Plan", "duration_days": 90, "roi_rate": 10.0},
        {"id": 4, "name": "Platinum Plan", "duration_days": 120, "roi_rate": 12.0},
        {"id": 5, "name": "Diamond Plan", "duration_days": 180, "roi_rate": 15.0},
        {"id": 6, "name": "Ultimate Plan", "duration_days": 365, "roi_rate": 20.0}
    ]
    
    if request.method == 'POST':
        # Get the selected plan and deposit amount from the form data
        plan_id = request.POST.get('plan_id')
        deposit_amount = request.POST.get('amount')
        
        # Look up the selected plan by its id
        selected_plan = next((plan for plan in plans if plan['id'] == int(plan_id)), None)

        if selected_plan:
            # Create Investment object for the user
            user_profile = request.user.userprofile
            plan = Plan.objects.get(id=selected_plan['id'])
            
            investment, created = Investment.objects.get_or_create(
                user_profile=user_profile,
                defaults={
                    'deposit_amount': Decimal(deposit_amount),
                    'roi_accumulated': Decimal('0.00'),
                    'plan': plan,
                }
            )

            # Trigger Celery task to update ROI in the background
            update_user_roi.delay(user_profile.id, deposit_amount)

            # Redirect to success page
            return render(request, 'investment/investment_success.html', {"selected_plan": selected_plan, "deposit_amount": deposit_amount})
        else:
            # If no plan was selected, show an error message
            return render(request, 'create_investment.html', {'error': 'Invalid plan selected', 'plans': plans})

    # Render the investment creation form with the available plans
    return render(request, 'investment/create_investment.html', {'plans': plans})