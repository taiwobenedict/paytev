from django.db import models

# Create your models here.

class AppInfo(models.Model):
    app_domain = models.CharField(
        max_length=50, 
        default='paytev.com', 
        help_text='Domain name of this site'
    )
    app_name = models.CharField(
        max_length=20, 
        default='Paytev'
    )
    phone = models.CharField(
        max_length=13, 
        default='', 
        help_text='Format: 2348144216361'
    )
    email = models.EmailField(
        default='princeooyes@gmail.com'
    )
    keywords = models.TextField(
        max_length=2000, 
        default='Paytev'
    )
    content_field = models.TextField(
        max_length=2000, 
        default='Paytev - Best VTU site', 
        help_text='Site Description'
    )
    app_logo = models.ImageField(
        default='', 
        null=True, 
        blank=True
    )
    paystack_sk_token = models.CharField(
        max_length=100, 
        default='', 
        blank=True, 
        null=True
    )
    paystack_pk_token = models.CharField(
        max_length=100, 
        default='', 
        blank=True, 
        null=True
    )
    paystack_amount_funding_percentage = models.FloatField(
        default=0.016, 
        help_text="0.016 means 1.6%, it is the commission Paystack will deduct"
    )
    bank_account_no = models.CharField(
        max_length=15, 
        default='2005309292'
    )
    bank_name = models.CharField(
        max_length=300, 
        default='Kuda Bank'
    )
    account_name = models.CharField(
        max_length=300, 
        default='VICTOR OYEDOKUN'
    )
    dashboard_extra_info = models.TextField(
        max_length=1000000, 
        default="", 
        blank=True, 
        null=True
    )
    admin_url = models.CharField(
        max_length=300, 
        default="admin"
    )

    def __str__(self):
        return self.app_name


class ActivationKeys(models.Model):
    activation_key = models.CharField(
        max_length=250
    )
    secret_key = models.CharField(
        max_length=50
    )
    activation_url = models.CharField(max_length=250)
    activated = models.BooleanField(default=False)
    
    
    