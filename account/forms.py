# account/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  
from django.core.validators import RegexValidator

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    pin = forms.CharField(
        max_length=4,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{4}$', 
                message="PIN must be exactly 4 digits, and must be numeric"
            )
        ]
    )

    class Meta:
        model = CustomUser  
        fields = ['username', 'email', 'phone_number', 'password1', 'password2', 'pin']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email is already in use')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Phone number already exists')
        return phone_number

    def clean_pin(self):
        pin = self.cleaned_data.get('pin')
        if not pin.isdigit():
            raise forms.ValidationError('PIN must be numeric')
        if len(pin) != 4:
            raise forms.ValidationError('PIN must be exactly 4 digits, and must be numeric')
        return pin




class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'}))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class PasswordResetForm(forms.Form):
    email = forms.EmailField(required=True)

class PasswordResetOTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'}))

class SetNewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data




class ImpersonateForm(forms.Form):
    user_id = forms.IntegerField(label='User ID to Impersonate')



class AdminWalletActionForm(forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label='Select User')
    action_choices = [('credit', 'Credit'), ('debit', 'Debit')]
    action = forms.ChoiceField(choices=action_choices, label='Action')
    wallet_choices = [('wallet_credit', 'Wallet Credit'), ('bonus_balance', 'Bonus Balance')]
    wallet_type = forms.ChoiceField(choices=wallet_choices, label='Wallet Type')
    amount = forms.DecimalField(label='Amount')
    narration = forms.CharField(label='Narration', max_length=255)






class AdminWalletActionForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label='Select User',
        widget=forms.Select(attrs={'class': 'user-select'})
    )
    action_choices = [('', 'Select Action'), ('credit', 'Credit'), ('debit', 'Debit')]
    action = forms.ChoiceField(choices=action_choices, label='Action')
    wallet_choices = [('', 'Select Wallet Type'), ('wallet_credit', 'Wallet Credit'), ('bonus_balance', 'Bonus Balance')]
    wallet_type = forms.ChoiceField(choices=wallet_choices, label='Wallet Type')
    amount = forms.DecimalField(label='Amount')
    narration = forms.CharField(label='Narration', max_length=255)






#Reset PIN forms
class ResetPinRequestForm(forms.Form):
    # Form for requesting a PIN reset
    email = forms.EmailField(required=True)

class ResetPinTokenForm(forms.Form):
    # Form for entering the reset token
    token = forms.CharField(max_length=32, required=True)

class ResetPinForm(forms.Form):
    # Form for entering new PIN
    new_pin = forms.CharField(
        max_length=4,
        required=True,
        validators=[RegexValidator(
            regex=r'^\d{4}$', message="PIN must be exactly 4 digits.")]
    )
    # Form for confirming new PIN
    confirm_pin = forms.CharField(
        max_length=4,
        required=True,
        validators=[RegexValidator(
            regex=r'^\d{4}$', message="PIN must be exactly 4 digits.")]
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get('new_pin')
        confirm_pin = cleaned_data.get('confirm_pin')

        # Check if the new PIN and confirm PIN match
        if new_pin and confirm_pin and new_pin != confirm_pin:
            raise forms.ValidationError('PINs do not match')
        return cleaned_data

#Profile forms 
from django import forms
from .models import CustomUser

# Profile forms 
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['address', 'bio', 'profile_picture', 'date_of_birth']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your address',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself',
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control',
            }),
        }
