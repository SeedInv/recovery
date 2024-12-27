# from django.contrib import admin
# from .models import Wallet, Recovery

# class RecoveryAdmin(admin.ModelAdmin):
#     # Define the fields to display in the list view
#     list_display = ('name', 'email', 'phone', 'wallet', 'loss_description', 'payment_method', 'lost_amount', 'recovery_phrase')
    
#     # Define the fields that can be used to filter the list view
#     list_filter = ('wallet', 'loss_description', 'payment_method')
    
#     # Enable searching by 'name', 'email', and 'phone' in the admin panel
#     search_fields = ('name', 'email', 'phone')
    
#     # Customize the form layout with fieldsets for grouping fields
#     fieldsets = (
#         (None, {
#             'fields': ('name', 'email', 'phone', 'wallet')
#         }),
#         ('Loss Details', {
#             'fields': ('loss_description', 'lost_amount', 'payment_method')
#         }),
#         ('Recovery Information', {
#             'fields': ('recovery_phrase',)
#         }),
#     )

# # Register the models with the admin site
# admin.site.register(Wallet)
# admin.site.register(Recovery, RecoveryAdmin)


from django.contrib import admin
from .models import Wallet, Recovery

class RecoveryAdmin(admin.ModelAdmin):
    # Define the fields to display in the list view, including date fields
    list_display = (
        'name', 'email', 'phone', 'wallet', 'loss_description',
        'payment_method', 'lost_amount', 'recovery_phrase', 
        'created_at', 'updated_at'
    )
    
    # Define the fields that can be used to filter the list view, including date fields
    list_filter = ('wallet', 'loss_description', 'payment_method', 'created_at', 'updated_at')
    
    # Enable searching by 'name', 'email', and 'phone' in the admin panel
    search_fields = ('name', 'email', 'phone')
    
    # Customize the form layout with fieldsets for grouping fields
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'wallet')
        }),
        ('Loss Details', {
            'fields': ('loss_description', 'lost_amount', 'payment_method')
        }),
        ('Recovery Information', {
            'fields': ('recovery_phrase',)
        }),
    )

# Register the models with the admin site
admin.site.register(Wallet)
admin.site.register(Recovery, RecoveryAdmin)
