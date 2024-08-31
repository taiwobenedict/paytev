from django import forms
from .models import AirtimePurchase, AirtimeAPIConfiguration

class AirtimeRechargeForm(forms.ModelForm):
    network_provider = forms.ChoiceField(choices=[], label='Network Provider')

    class Meta:
        model = AirtimePurchase
        fields = ['phone_number', 'amount', 'network_provider']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Enter amount'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch active network configurations and populate the network_provider field
        networks = AirtimeAPIConfiguration.objects.filter(is_active=True)
        network_choices = [(config.network_identifier_code, config.network_name) for config in networks]
        network_choices.insert(0, ('', 'Select network'))  # Add a default choice
        self.fields['network_provider'].choices = network_choices
