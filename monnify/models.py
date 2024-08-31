from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
import json
import random
import string
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

User = get_user_model()


class MonnifyConfig(models.Model):
    base_url = models.URLField(default='https://sandbox.monnify.com/api/v1/')
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    contract_code = models.CharField(max_length=255)
    fee = models.FloatField(default=0.015, help_text=mark_safe(
        "<strong style='color:red;'>This shoulg be a percentage of the amount the user buys</strong>"))
    wallet_account_number = models.CharField(
        max_length=20, blank=True, null=True)

    def __str__(self):
        return self.contract_code

    def generate_account_reference(self):
        """Generate a random 10-character string for account reference."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=15))
"""

user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_reference = models.CharField(max_length=50, default='', unique=True)
    account_number = models.CharField(max_length=500, default='')
    currency_code = models.CharField(max_length=50, default='')
    contract_code = models.CharField(max_length=50, default='')
    account_name = models.CharField(max_length=500, default='')
    customer_email = models.CharField(max_length=50, default='')
    bank_name = models.CharField(max_length=500, default='')
    bank_code = models.CharField(max_length=500, default='')
    reservation_reference = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='')
    created_on = models.DateTimeField(auto_now_add=True)
    bvn = models.CharField(max_length=500, default='')
"""

class VirtualAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=500, default='')
    bank_name = models.CharField(max_length=500, default='')
    account_name = models.CharField(max_length=100)
    account_reference = models.CharField(
        max_length=50, default='', unique=True)
    reservation_reference = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    response_body = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.account_name} - {self.bank_name} ({self.account_number})"
    
    
class ProcessedNotification(models.Model):
    transaction_reference = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_reference
