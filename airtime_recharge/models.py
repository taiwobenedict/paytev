from django.db import models
from account.models import CustomUser

class AirtimePurchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    network_provider = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    old_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    api_response = models.TextField(null=True, blank=True)
    request_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Airtime purchase #{self.id} for {self.phone_number}"






from django.db import models

class AirtimeAPIConfiguration(models.Model):
    api_name = models.CharField(max_length=30, default='MTN')
    is_active = models.BooleanField(default=False)
    network_image = models.ImageField(upload_to='network_images/', default="", help_text="the best image needed here is a square image recommended is 500 x 500")
    identifier = models.CharField(max_length=50, default='mtn_airtime', help_text='this should be a unique identifier')
    api_url = models.TextField(max_length=1000, default='https://api-service.vtpass.com/api/pay')
    api_data = models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data": {"serviceID": "mtn", "amount": "amount_float", "phone": "phone_number", "request_id": "request_id"}, "headers": {"Authorization": "Basic UHJpbmNlb295ZXNAZ21haWwuY29tOjFQYXl0ZXZUZWFt"}}')
    success_code = models.CharField(max_length=500, default='true')
    network_name = models.CharField(max_length=50, default='MTN', help_text='Network name for display')
    network_identifier_code = models.CharField(max_length=50, default='1', help_text='The network code or identifier (ID) used by the API')

    def __str__(self):
        return self.api_name
