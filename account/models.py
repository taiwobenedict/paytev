# account/models.py 
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver 
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from PIL import Image
from django.core.files import File
from tempfile import NamedTemporaryFile
import logging, os
logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, blank=True)
    email = models.EmailField(unique=True)
    wallet_credit = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    bonus_balance = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    pending_balance = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    pin = models.CharField(
        max_length=4,
        validators=[RegexValidator( regex=r'^\d{4}$', message="PIN must be exactly 4 digits.")]
    )
    reset_token = models.CharField(max_length=32, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True) 
    kyc_status = models.CharField(max_length=20, default='Not Verified')
    
    REQUIRED_FIELDS = ['phone_number']

    def update_wallet_credit(self, amount):
        self.wallet_credit += float(amount)
        self.save()

    def save(self, *args, **kwargs):
        if self.profile_picture:
            image = Image.open(self.profile_picture)
            if image.height > 300 or image.width > 300:
                output_size = (300, 300)
                image.thumbnail(output_size)
                temp_file = NamedTemporaryFile(delete=False)
                image.save(temp_file, format='JPEG')
                temp_file.seek(0)
                self.profile_picture.save(os.path.basename(self.profile_picture.name), File(temp_file), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


# Signal to ensure balances are initialized properly upon signup
logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def initialize_user_data(sender, instance, created, **kwargs):
    if created:
        logger.info(f'Initializing data for user: {instance.email}')
        # Initialize wallet balances
        instance.wallet_credit = 0.00
        instance.bonus_balance = 0.00
        instance.pending_balance = 0.00
        instance.save()
        
        # Initialize KYC status
        from kyc.models import KYC
        KYC.objects.create(user=instance, status='Not Verified')
        logger.info(f'Initialized KYC status to Not Verified for user: {instance.email}')
        


class OTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.otp_code}"

class UserOTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f'{self.user.email} - {self.otp}'



class CreditWalletTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)  # e.g., 'credit', 'debit'
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"



class BonusWalletTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)  # e.g., 'credit', 'debit'
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"
        


