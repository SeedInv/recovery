import logging
from django.shortcuts import render, redirect
from .models import WalletAsset, ConnectWallet
from .forms import ConnectWalletForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from django.conf import settings
import smtplib

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def select_wallet(request):
    # Get all available wallets (WalletAsset)
    wallets = WalletAsset.objects.all()

    # Get the user's currently connected wallets
    connected_wallets = ConnectWallet.objects.filter(user=request.user)

    # Debug: Log the user's currently connected wallets
    logger.debug(f"User {request.user.username} has {connected_wallets.count()} connected wallets.")

    # Handle POST request (when the form is submitted)
    if request.method == 'POST':
        logger.debug(f"POST data received: {request.POST}")
        form = ConnectWalletForm(request.POST)
        
        if form.is_valid():
            logger.debug("Form is valid. Attempting to save ConnectWallet instance.")
            # Save the ConnectWallet instance for the user
            connect_wallet = form.save(commit=False)
            connect_wallet.user = request.user  # Associate the current user
            connect_wallet.save()  # Save the ConnectWallet instance
            logger.info(f"ConnectWallet instance saved for user {request.user.username}.")

            # Try to send email to the user and the admin
            try:
                # Send email to the user
                send_mail(
                    subject="Wallet Connected Successfully",
                    message=f"Hello {request.user.username},\n\nYour wallet ({connect_wallet.wallet.name}) has been successfully connected.\n\nThank you!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                # Send email to the admin
                admin_email = 'admin@example.com'  # Replace with your admin email or get it dynamically
                send_mail(
                    subject=f"New Wallet Connected by {request.user.username}",
                    message=f"Hello Admin,\n\nUser {request.user.username} has connected a new wallet: {connect_wallet.wallet.name}.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
                logger.info("Emails sent successfully to user and admin.")
            except smtplib.SMTPException as e:
                # Log SMTP errors
                logger.error(f"SMTP error occurred while sending email: {e}")
                # Optionally, show a user-friendly message or notify admin
                return render(request, 'connectwallet/connect_wallet.html', {
                    'form': form,
                    'wallets': wallets,
                    'connected_wallets': connected_wallets,
                    'error_message': 'There was an issue sending the confirmation email. Please try again later.'
                })
            except BadHeaderError as e:
                # Handle BadHeaderError (if the email header is invalid)
                logger.error(f"Bad header error: {e}")
                return render(request, 'connectwallet/connect_wallet.html', {
                    'form': form,
                    'wallets': wallets,
                    'connected_wallets': connected_wallets,
                    'error_message': 'There was an issue with the email format. Please try again later.'
                })
            except Exception as e:
                # Catch any other exceptions and log them
                logger.error(f"Unexpected error occurred while sending email: {e}")
                return render(request, 'connectwallet/connect_wallet.html', {
                    'form': form,
                    'wallets': wallets,
                    'connected_wallets': connected_wallets,
                    'error_message': 'An unexpected error occurred. Please try again later.'
                })

            # Redirect back to the same page after adding a wallet
            return redirect('select_wallet')  
        else:
            logger.warning("Form is invalid. Errors:")
            for field, errors in form.errors.items():
                logger.warning(f"{field}: {', '.join(errors)}")
    else:
        logger.debug("GET request received.")
        form = ConnectWalletForm()

    # Render the page, including all wallets and connected wallets
    return render(request, 'connectwallet/connect_wallet.html', {
        'form': form,
        'wallets': wallets,
        'connected_wallets': connected_wallets,  # Display the user's connected wallets
    })
