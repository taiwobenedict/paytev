from django import forms
from .models import KYC

class KYCForm(forms.ModelForm):
    VERIFICATION_CHOICES = [
        ('', 'Select'),
        ('BVN', 'BVN'),
        ('NIN', 'NIN'),
        ('Both', 'Both'),
    ]

    verification_type = forms.ChoiceField(
        choices=VERIFICATION_CHOICES, 
        required=True, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    bvn = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'BVN'})
    )
    nin = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIN'})
    )

    class Meta:
        model = KYC
        fields = [
            'first_name', 'last_name', 'middle_name', 'date_of_birth',
            'phone_number', 'residential_address',
            'verification_type', 'bvn', 'nin', 'id_type', 'id_number',
            'bank_name', 'account_number', 'next_of_kin_name', 
            'next_of_kin_relationship', 'next_of_kin_phone', 'declaration'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name', 'required': False}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'residential_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Residential Address'}),
            'id_type': forms.Select(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Number'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            'next_of_kin_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Next of Kin Name'}),
            'next_of_kin_relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Next of Kin Relationship'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Next of Kin Phone'}),
            'declaration': forms.CheckboxInput()
        }

    def __init__(self, *args, **kwargs):
        super(KYCForm, self).__init__(*args, **kwargs)
        # Set all fields as required except the middle name
        for field_name in self.fields:
            if field_name != 'middle_name':
                self.fields[field_name].required = True
            else:
                self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()
        verification_type = cleaned_data.get('verification_type')

        if verification_type == 'BVN':
            if not cleaned_data.get('bvn'):
                self.add_error('bvn', 'BVN is required.')
        elif verification_type == 'NIN':
            if not cleaned_data.get('nin'):
                self.add_error('nin', 'NIN is required.')
        elif verification_type == 'Both':
            if not cleaned_data.get('bvn'):
                self.add_error('bvn', 'BVN is required.')
            if not cleaned_data.get('nin'):
                self.add_error('nin', 'NIN is required.')
