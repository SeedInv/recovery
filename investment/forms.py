# from django import forms
# from .models import Investment, Plan

# class InvestmentForm(forms.ModelForm):
#     plan_id = forms.ModelChoiceField(queryset=Plan.objects.all(), label="Select Investment Plan", empty_label=None)
#     amount = forms.DecimalField(max_digits=15, decimal_places=2, label="Deposit Amount", min_value=0.01)

#     class Meta:
#         model = Investment
#         fields = ['plan_id', 'deposit_amount']


from django import forms
from .models import Investment, Plan

class InvestmentForm(forms.ModelForm):
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.all(),
        label="Select Investment Plan",
        empty_label=None
    )
    deposit_amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Deposit Amount",
        min_value=0.01
    )

    class Meta:
        model = Investment
        fields = ['plan', 'deposit_amount']  # Ensure these match model field names

