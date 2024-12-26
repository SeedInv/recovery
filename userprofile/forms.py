
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile
from django_countries.fields import CountryField
from django.contrib.auth import authenticate


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    username = forms.CharField(max_length=150, required=True, help_text="Enter a unique username.")
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'}))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}))
    profile_image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'placeholder': 'Upload your profile image'}))
    wallet_address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your wallet address'}))
    country = CountryField(blank_label='(Select Country)').formfield(required=True, widget=forms.Select())
    address = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your address', 'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if not username:
            self.add_error('username', "The username field is required.")
        if not email:
            self.add_error('email', "The email field is required.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()

        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.phone_number = self.cleaned_data.get('phone_number')
        user_profile.profile_image = self.cleaned_data.get('profile_image')
        user_profile.wallet_address = self.cleaned_data.get('wallet_address')
        user_profile.country = self.cleaned_data.get('country')
        user_profile.address = self.cleaned_data.get('address')
        if commit:
            user_profile.save()

        return user




class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # Authenticate the user during form validation
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Invalid username or password.")
        else:
            raise ValidationError("Both username and password are required.")

        return cleaned_data
