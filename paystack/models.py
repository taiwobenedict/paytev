# paystack/models.py

from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal


User = get_user_model()


class PaystackConfiguration(models.Model):
    public_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    paystack_charge = models.DecimalField(
    max_digits=5, 
    decimal_places=3, 
    default=Decimal('0.016'), 
    help_text="Enter the Paystack charge percentage. (e.g., 1.6 for 1.6%)"
)


    def __str__(self):
        return "Paystack Configuration"



class PaystackTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='pending')  
    wallet_before = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wallet_after = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f'Transaction {self.reference} by {self.user}'
    
    
