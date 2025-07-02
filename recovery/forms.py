
from django import forms
from .models import Recovery

class RecoveryForm(forms.ModelForm):
    class Meta:
        model = Recovery
        fields = ['name', 'email', 'phone', 'loss_description', 'lost_amount', 'payment_method']

    def __init__(self, *args, **kwargs):
        super(RecoveryForm, self).__init__(*args, **kwargs)
        # Add the 'form-control' class to all fields for consistent styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
