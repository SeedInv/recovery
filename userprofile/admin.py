

from django.contrib import admin
from .models import UserProfile
from django.utils.html import format_html

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'get_username', 
        'get_email', 
        'get_first_name', 
        'get_last_name', 
        'phone_number', 
        'wallet_address', 
        'country', 
        'address', 
        'profile_image_preview',  # Display the profile image
        'created_at',  # Display the created_at field
        'updated_at'   # Display the updated_at field
    )
    search_fields = ('user__username', 'user__email', 'phone_number', 'wallet_address')
    
    # Make these fields editable in the list view
    list_editable = ('phone_number', 'wallet_address', 'country', 'address')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

    # Method to display the profile image in the list view
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_image.url)
        return "No image"
    profile_image_preview.short_description = 'Profile Image'
