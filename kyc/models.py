# kyc/models.py
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from account.models import CustomUser





NIGERIA_STATES = [
    ('AB', 'Abia'), ('AD', 'Adamawa'), ('AK', 'Akwa Ibom'), ('AN', 'Anambra'), ('BA', 'Bauchi'),
    ('BY', 'Bayelsa'), ('BE', 'Benue'), ('BO', 'Borno'), ('CR', 'Cross River'), ('DE', 'Delta'),
    ('EB', 'Ebonyi'), ('ED', 'Edo'), ('EK', 'Ekiti'), ('EN', 'Enugu'), ('GO', 'Gombe'),
    ('IM', 'Imo'), ('JI', 'Jigawa'), ('KD', 'Kaduna'), ('KN', 'Kano'), ('KT', 'Katsina'),
    ('KE', 'Kebbi'), ('KO', 'Kogi'), ('KW', 'Kwara'), ('LA', 'Lagos'), ('NA', 'Nasarawa'),
    ('NI', 'Niger'), ('OG', 'Ogun'), ('ON', 'Ondo'), ('OS', 'Osun'), ('OY', 'Oyo'),
    ('PL', 'Plateau'), ('RI', 'Rivers'), ('SO', 'Sokoto'), ('TA', 'Taraba'), ('YO', 'Yobe'),
    ('ZA', 'Zamfara'), ('FC', 'Federal Capital Territory')
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

ID_TYPE_CHOICES = [
    ('NIN', 'NIN Slip'),
    ('National ID', 'National ID (Plastic)'),
    ('Driver’s License', 'Driver’s License'),
    ('Passport', 'International Passport'),
    ('Voter’s Card', 'Voter’s Card'),
]

STATUS_CHOICES = [
    ('Not Verified', 'Not Verified'),
    ('Submitted', 'Submitted'),
    ('Verified', 'Verified'),
    ('Rejected', 'Rejected'),
]

class KYC(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    # Personal Information
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    middle_name = models.CharField(max_length=50, blank=True,)
    date_of_birth = models.DateField(null=True)
    
    phone_number = models.CharField(max_length=15)
    residential_address = models.TextField(blank=True)
    
    
    # Identification Information
    verification_type = models.CharField(max_length=10, choices=[('BVN', 'BVN'), ('NIN', 'NIN'), ('Both', 'Both')], default='Select')
    bvn = models.CharField(max_length=11, blank=True)
    nin = models.CharField(max_length=11, blank=True)
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES)
    id_number = models.CharField(max_length=20)
    
    # Bank Account Information
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=10)
    
    # Next of Kin Information
    next_of_kin_name = models.CharField(max_length=100)
    next_of_kin_relationship = models.CharField(max_length=50)
    next_of_kin_phone = models.CharField(max_length=15)

    # Consent & Declaration
    declaration = models.BooleanField(default=False)
    
    # KYC Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Verified')
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

from .models import KYC
@receiver(post_save, sender=KYC)
def update_user_kyc_status(sender, instance, **kwargs):
    user = instance.user
    user.kyc_status = instance.status
    user.save()
    

    def __str__(self):
        return f"{self.user.username} - {self.first_name} {self.last_name}"




class KYCSettings(models.Model):
    kyc_charge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return "KYC Settings"

    class Meta:
        verbose_name = "KYC Settings"
        verbose_name_plural = "KYC Settings"
