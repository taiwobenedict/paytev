# paystack/forms.py

from django import forms
from decimal import Decimal

class FundWalletForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        label='Amount',
        widget=forms.NumberInput(attrs={'placeholder': 'Enter amount to fund'})
    )
