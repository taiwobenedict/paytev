from django.db import models

# Create your models here.
import time
import random
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.utils import timezone
from account.models import CustomUser
from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL

CHOICES = (
    ("QUEUE", "QUEUE"),
    ("FAILED", "FAILED"),
    ("REFUNDED", "REFUNDED"),
   	("SUCCESS", "SUCCESS"),
)


class Transactions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_transactions")
    status = models.CharField(max_length=50, blank=True, null=True)
    identifier = models.CharField(default="", max_length=50)
    bill_type = models.CharField(max_length=500, blank=True, null=True)
    bill_code = models.CharField(max_length=500, blank=True, null=True)
    bill_number = models.CharField(max_length=300, blank=True, null=True)
    bill_serial = models.CharField(max_length=500, blank=True, null=True)
    bill_provider = models.CharField(max_length=500, blank=True, null=True)
    actual_amount = models.FloatField(default=0.0)
    paid_amount = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)
    old_balance = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)
    comment = models.CharField(max_length=500, blank=True, null=True)
    reference = models.CharField(max_length=300, blank=True, null=True)
    customernumber = models.CharField(
        default='', max_length=30, blank=True, null=True)
    customername = models.CharField(
        default='', max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    customer_dt_number = models.CharField(
        max_length=100, default='', blank=True, null=True)

    

    api_id = models.IntegerField(blank=True, null=True)

    # for account funding
    smsangosbulkcredit = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="wallet_funding", null=True, blank=True)
    amtcredited = models.FloatField(blank=True, null=True)
    # end for account funding

    api_response = models.TextField(max_length=20000, blank=True, null=True)
    callback_url = models.TextField(max_length=20000, blank=True, null=True)
    callback_done = models.BooleanField(default=False)
    mode = models.CharField(max_length=200, default="DIRECT")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


@receiver(pre_save, sender=Transactions)
def transaction_pre_save_receiver(sender, **kwargs):
    instance = kwargs['instance']
    print(instance, kwargs)
    if instance and not kwargs['update_fields']:
        try:
            t = Transactions.objects.all()
            if t.count() > 0:
                getLastOne = t.last()
                print(int(timezone.now().timestamp()) -
                      int(getLastOne.created_at.timestamp()), "sept")
                if (int(timezone.now().timestamp()) - int(getLastOne.created_at.timestamp()) <= 5) \
                        and (getLastOne.user == instance.user) and (instance.bill_number == getLastOne.bill_number) and\
                        instance.status == "SUCCESS" and instance.mode != "API":
                    raise ValidationError("Wait Please")
                else:
                    pass
            else:
                pass

        except Exception as e:
            raise e
    else:
        pass
