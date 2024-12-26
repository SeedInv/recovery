from django.contrib import admin
from .models import Plan, Transaction, Investment, WithdrawalRequest

# Customize the Transaction model in the admin
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'status', 'created_at', 'description')
    list_filter = ('transaction_type', 'status')  # Add filters to the sidebar
    search_fields = ('user__username', 'transaction_type', 'description')  # Add search functionality
    ordering = ('-created_at',)  # Order by latest created_at by default

# Customize the Investment model in the admin
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'deposit_amount', 'roi_accumulated', 'deposit_time', 'last_updated', 'is_active', 'get_plan')
    list_filter = ('is_active', 'plan')  # Add filtering by plan
    search_fields = ('user_profile__user__username', 'deposit_amount', 'plan__name')  # Search functionality for plan names
    ordering = ('-deposit_time',)

    def get_user(self, obj):
        """
        Custom method to get the username from the related UserProfile
        """
        return obj.user_profile.user.username
    get_user.short_description = 'User'  # Custom column header in the admin list view

    def get_plan(self, obj):
        """
        Custom method to get the name of the Plan from the related Plan model
        """
        return obj.plan.name if obj.plan else 'No Plan'
    get_plan.short_description = 'Plan'  # Custom column header for the plan field in the list view

# Customize the WithdrawalRequest model in the admin
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'amount', 'created_at', 'approved')
    list_filter = ('approved',)  # Filter by approval status
    search_fields = ('user_profile__user__username', 'amount')
    ordering = ('-created_at',)  # Ensure new requests appear first by ordering by created_at

    # Custom method to get the username from the related UserProfile
    def get_user(self, obj):
        """
        Custom method to get the username from the related UserProfile
        """
        return obj.user_profile.user.username
    get_user.short_description = 'User'  # Custom column header in the admin list view

    # Add a custom admin action to manually approve the withdrawal request
    def approve_withdrawal_request(self, request, queryset):
        # Manually approve withdrawal request and update the status
        for withdrawal in queryset:
            if not withdrawal.approved:
                withdrawal.approved = True
                withdrawal.save()

                # Create the corresponding transaction for the approved withdrawal
                Transaction.objects.create(
                    user=withdrawal.user_profile.user,
                    amount=withdrawal.amount,
                    transaction_type='withdrawal',
                    status='approved',
                    description="Approved Withdrawal"
                )

                # Deduct the withdrawal amount from the user's balance
                user_profile = withdrawal.user_profile
                user_profile.balance -= withdrawal.amount
                user_profile.save()

    approve_withdrawal_request.short_description = "Manually approve selected withdrawal requests"  # Custom action description

    actions = ['approve_withdrawal_request']  # Register the action in the admin

# Register the customized admin classes
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)
admin.site.register(Plan)  # Don't forget to register the Plan model
