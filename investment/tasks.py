from celery import shared_task
from decimal import Decimal
from django.utils.timezone import now as timezone_now
from .models import Investment, Transaction, Plan
import logging
from userprofile.models import UserProfile  # Import UserProfile model (assuming it's in the 'users' app)

logger = logging.getLogger(__name__)

@shared_task
def update_user_roi(user_profile_id, deposit_amount):
    try:
        # Fetch user profile and related plan
        user_profile = UserProfile.objects.get(id=user_profile_id)
        default_plan = Plan.objects.first()  # Or apply your own logic to get the default plan
        
        if not default_plan:
            logger.error("No investment plan available for user: %s", user_profile.user.username)
            return "No investment plan available."
        
        # Get or create investment for user
        investment, created = Investment.objects.get_or_create(
            user_profile=user_profile,
            defaults={
                'deposit_amount': Decimal(deposit_amount),
                'roi_accumulated': Decimal('0.00'),
                'plan': default_plan,
            }
        )

        # Calculate ROI increment
        roi_increment = investment.deposit_amount * Decimal(str(default_plan.roi_rate)) / 100  # ROI based on plan rate
        if roi_increment <= 0:
            logger.warning("ROI increment calculation resulted in 0 or negative for user: %s", user_profile.user.username)
            return "ROI calculation error."

        # Update accumulated ROI
        investment.roi_accumulated += roi_increment
        investment.last_updated = timezone_now()
        investment.save()

        # Record the transaction for ROI
        Transaction.objects.create(
            user=user_profile.user,
            transaction_type='roi',
            amount=roi_increment,
            status='approved',
            created_at=timezone_now(),
            description=f"ROI of ${roi_increment} earned from deposit of ${investment.deposit_amount}."
        )

        # Log success
        logger.info("ROI updated successfully for user: %s, New ROI: %s", user_profile.user.username, investment.roi_accumulated)
        return f"ROI updated successfully. New ROI: {investment.roi_accumulated}"

    except Exception as e:
        logger.error(f"Error updating ROI for user: {user_profile.user.username} - {str(e)}")
        return f"Error: {str(e)}"
