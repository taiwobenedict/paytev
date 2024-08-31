# strowallet/models.py
from django.db import models
from django.conf import settings

class StrowalletConfig(models.Model):
    public_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    charge_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return "Strowallet Configuration"

class StrowalletAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=20)
    customer_email = models.EmailField()

    def __str__(self):
        return f"{self.user.username} - {self.account_number} - {self.account_name}"


class Hooklog(models.Model):
    myhook = models.CharField(max_length=255, unique=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.myhook
