from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User 
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError
from .models import UserProfile 

# Registration View
# userprofile/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistrationForm

# userprofile/views.py
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import login

from django.shortcuts import render, redirect
from .forms import RegistrationForm

import logging

# Get a logger instance
logger = logging.getLogger(__name__)

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        
        # Log POST data and uploaded files for debugging
        logger.debug(f"POST Data: {request.POST}")
        logger.debug(f"FILES Data: {request.FILES}")

        if form.is_valid():
            try:
                # Use the form's save method to create user and user profile
                user = form.save(commit=True)

                # Log the created user for debugging
                logger.debug(f"User created: {user.username} ({user.email})")

                # Send a success email
                send_mail(
                    subject="Registration Successful",
                    message=f"Hello {form.cleaned_data['first_name']},\n\n"
                            "Your registration was successful. Welcome to our platform!",
                    from_email="no-reply@example.com",  # Replace with your email
                    recipient_list=[form.cleaned_data['email']],
                    fail_silently=False,
                )

                # Display success message and redirect
                messages.success(request, "Registration successful. Check your email for confirmation.")
                return redirect('login')

            except IntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                messages.error(request, "A user with these details already exists.")
                
        else:
            # Log form errors
            logger.error(f"Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = RegistrationForm()

    return render(request, "userprofile/register.html", {"form": form})



def login_view(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        # Redirect the user to their profile page (or another page)
        return redirect('profile')  # Replace 'profile' with your actual profile URL name

    # Handle the POST request for login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        # If authentication is successful, log the user in and redirect them to their profile page
        if user is not None:
            login(request, user)
            return redirect('profile')  # Redirect to the profile page after login
        else:
            # If authentication fails, return an error message
            return render(request, 'userprofile/login.html', {'error': 'Invalid credentials'})

    # Handle the GET request (initial login page)
    return render(request, 'userprofile/login.html')



@login_required
def profile_view(request):
    # Access the user's profile and balance
    user_profile = request.user.userprofile  # This accesses the UserProfile related to the logged-in user
    user_balance = user_profile.balance  # Get the user's balance from the UserProfile

    # Pass all relevant user profile details to the template
    return render(request, 'userprofile/profile.html', {
        'user_balance': user_balance,
        'user_profile': user_profile,  # Pass the full user profile to the template
    })




# Logout View
def logout_view(request):
    logout(request)  # This clears the session and logs the user out
    return redirect('home')  # Redirect to a homepage or login page



# PASSWORD RESET 
# Password reset request view (you already have this)
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseServerError
from django.contrib import messages

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            
            if not users.exists():
                # Optionally, display a message saying no user found.
                messages.error(request, "No user found with this email address.")
                return render(request, 'userprofile/password_reset.html', {'form': form})
            
            for user in users:
                try:
                    # Generate token and uid
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(str(user.pk).encode('utf-8'))

                    # Create reset URL
                    domain = get_current_site(request).domain
                    protocol = "https" if request.is_secure() else "http"
                    reset_url = f"{protocol}://{domain}/userprofile/reset/{uid}/{token}/"
                    
                    # Prepare email content
                    context = {
                        'user': user,
                        'reset_url': reset_url,
                    }
                    email_body = render_to_string('userprofile/password_reset_email.html', context)

                    # Send email
                    send_mail(
                        'Password Reset Request',
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )

                except BadHeaderError:
                    # Handle any header-related issues in the email
                    messages.error(request, "There was an error with the email header.")
                    return render(request, 'userprofile/password_reset.html', {'form': form})
                except Exception as e:
                    # Catch any other exceptions (e.g., SMTP issues)
                    messages.error(request, f"An error occurred while sending the email: {str(e)}")
                    return render(request, 'userprofile/password_reset.html', {'form': form})

            # Inform the user that the reset email has been sent (even if the email is not valid)
            messages.success(request, "If an account with that email exists, you will receive a password reset link shortly.")
            return render(request, 'password_reset_done.html')
        else:
            # Handle form invalid case
            messages.error(request, "There were some errors with the form. Please try again.")
            return render(request, 'userprofile/password_reset.html', {'form': form})
    else:
        form = PasswordResetForm()
    
    return render(request, 'userprofile/password_reset.html', {'form': form})


# Password reset confirm view (where the user sets their new password)
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_encode(uidb64.encode()).decode('utf-8')
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        
        return render(request, 'userprofile/password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'userprofile/password_reset_invalid.html')

# Password reset done view (inform the user that the reset email has been sent)
def password_reset_done(request):
    return render(request, 'userprofile/password_reset_done.html')

# Password reset complete view (inform the user that the password was successfully reset)
def password_reset_complete(request):
    return render(request, 'userprofile/password_reset_complete.html')