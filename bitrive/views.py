from django.shortcuts import render
from django.http import HttpResponse
from userprofile.models import UserProfile
from userprofile.forms import RegistrationForm 



def home(request):
    # Initialize the context dictionary
    context = {
        'message': 'Welcome to Bitrive!',
    }

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Try to get the user's profile from the UserProfile model
        try:
            profile = UserProfile.objects.get(id=request.user.id)
        except UserProfile.DoesNotExist:
            profile = None  # If no profile exists, set profile to None

        # Add user first name and profile image to the context
        context['user_first_name'] = request.user.first_name
        context['profile'] = profile
        context['is_logged_in'] = True  # For showing the logged-in state in the template
    else:
        context['is_logged_in'] = False  # For showing the logged-out state in the template

    return render(request, 'bitrive/base.html', context)


def get_started(request):
    form = RegistrationForm()  # Instantiate the form
    return render(request, 'userprofile/register.html', {'form': form,})


def funds_recovery(request):
    return render(request, 'bitrive/funds_recovery.html')

def about(request):
    return render(request, 'bitrive/about.html')

def services(request):
    return render(request, 'bitrive/services.html')

def investment(request):
    return render(request, 'bitrive/investment.html')

def contact(request):
    return render(request, 'bitrive/contact.html')

def team(request):
    return render(request, 'bitrive/team.html')

def set_language_cookie(request):
    # Let's assume the user selects a language (for example: 'English')
    response = HttpResponse("Language set")
    # Set a cookie named 'preferred_language' with the user's chosen language
    response.set_cookie('preferred_language', 'English', max_age=3600)  # The cookie expires in 1 hour
    return response


def change_language(request):
    # Get the selected language from the form or URL parameter
    language = request.GET.get('language', 'English')  # Default to 'English' if not provided

    # Set a cookie for the selected language
    response = HttpResponse(f"Language changed to {language}")
    response.set_cookie('preferred_language', language, max_age=3600)  # Set cookie for 1 hour

    return response


def set_custom_cookie(request):
    response = HttpResponse("Setting a custom cookie")
    response.set_cookie('preferred_language', 'English', max_age=3600)  # Cookie expires after 1 hour
    return response





