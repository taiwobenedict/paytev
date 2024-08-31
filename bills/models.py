#Bills models.py

from django.db import models
import pytz
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, post_migrate
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
#from user_transactions.models import AllUserTransactionsLogs
from django.utils import timezone
import random
import time
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

class DataPlansPrices(models.Model):
    mtn = models.TextField(default='', max_length='1000',
                           blank=True, null=True)
    airtel = models.TextField(
        default='', max_length='1000', blank=True, null=True)
    glo = models.TextField(default='', max_length='1000',
                           blank=True, null=True)
    nine_mobile = models.TextField(
        default='', max_length='1000', blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return ("Data Prices")

class RechargeAirtimeAPI(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    #provider = models.CharField(max_length=1000, default='https://example.com')
    is_active = models.BooleanField(default=False)
    network_image = models.ImageField(
        default="", help_text="the best image needed here is a square image recommended is 49 x 49px")
    identifier = models.CharField(
        max_length=50,   default='waec_airtime', help_text='this should be a unique identifier')
    api_url = models.TextField(
        max_length=1000, default='https://apiname.online/api/airtime')
    api_url_data = models.JSONField(
        default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[YOUR_API_KEY]", "userid":"[USER_ID]", "network_id":"[network_code]", "amount":"[amt]", "phoneno":"[phone]"}, "headers":{"authorization": "Bearer (API_KEY)"}}, then edit suit you')
    api_url_balance = models.TextField(
        max_length=1000, default='https://apiname.online/api/balance?userid=[Enter_userid]&apikey=[Apikey]')
    user_discount = models.FloatField(default=0.0, help_text=mark_safe(
        "<strong style='color:red;'>This shoulg be a percentage of the amount the user buys</strong>"))
    success_code = models.CharField(max_length=500, default='true')
    description = models.TextField(default='<h4 id="note"><strong><u>How to Top-Up Airtime</u></strong></h4><p>TOP-UP your MTN, 9MOBILE, AIRTEL, GLO</p><p><li>Choose your Network</li><li>Enter your Recharge Amount</li><li>Enter the Phone number to recharge</li></p><p><strong>The more you recharge, the more bonus point you gathered</strong></p>', help_text="Html is allowed here")

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Airtime Recharge'
        verbose_name_plural = 'APIs For Airtime Recharge'


class DataNetworks(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    provider = models.CharField(max_length=1000, default='https://example.com')
    is_active = models.BooleanField(default=False)
    network_image = models.ImageField(
        default="", help_text="the best image needed here is a square image recommended is 49 x 49px")
    identifier = models.CharField(
        max_length=50,  default='waec_airtime', help_text='this should be a unique identifier')
    api_url = models.TextField(
        max_length=1000, default='https://apiname.online/api/databundle')
    api_url_data = models.JSONField(
        default=dict, help_text='e.g: copy and paste this => {"data":{"apikey":"[YOUR_API_KEY]", "userid":"[USER_ID]", "network_id":"[urlvariable]", "amount":"[apiamount]", "datacode":"[dataplan]","phoneno":"[phone]"}, "headers":{"authorization":"Bearer API_KEY"}}, then edit suit you')
    api_url_balance = models.TextField(
        max_length=1000, default='https://apiname.online/api/balance?userid=[Enter_userid]&apikey=[Apikey]')
    success_code = models.CharField(max_length=500, default='true')
    network_data_amount_json = models.TextField(max_length=13000, default='220|500MB_(SME)|1|500MB (SME)@NGN220|extravariable,410|1GB_(SME)|1|1GB (SME)@NGN410|extravariable',
                                                help_text=mark_safe("<strong style='color:red;'>apiamount|data_amount|portal_api_code|what_user_sees|extravariable'</strong>"))
    description = models.TextField(default='<h4 id="note"><strong><u>How to Top-Up Airtime</u></strong></h4><p>TOP-UP your MTN, 9MOBILE, AIRTEL, GLO</p><p><li>Choose your Network</li><li>Enter your Recharge Amount</li><li>Enter the Phone number to recharge</li></p><p><strong>The more you recharge, the more bonus point you gathered</strong></p>', help_text="Html is allowed here")

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Data Recharge'
        verbose_name_plural = 'APIs For Data Recharge'


class CableRecharegAPI(models.Model):
    api_name = models.CharField(max_length=30, default='apiname')
    is_active = models.BooleanField(default=False)
    provider = models.CharField(max_length=1000, default='https://example.com')
    api_url = models.TextField(
        max_length=1000, default='https://apiname.online/api/cable')
    identifier = models.CharField(
        max_length=50, default='startimes', help_text='this should be a unique identifier')
    service_id = models.CharField(
        max_length=50, default='waec_airtime', help_text='this should be a unique identifier')
    agent_discount = models.FloatField(default=0.0, help_text=mark_safe(
        "<strong style='color:red;'>This shoulg be a percentage of the amount the user buys</strong>"))
    user_discount = models.FloatField(default=0.0, help_text=mark_safe(
        "<strong style='color:red;'>This shoulg be a percentage of the amount the user buys</strong>"))
    referrer_bonus = models.FloatField(default=0.0, help_text=mark_safe(
        "<strong style='color:red;'>This shoulg be a percentage of the amount the user buys</strong>"))
    vtoken = models.CharField(
        max_length=100, default='Basic XXXXXXXXXX', help_text='this should be a unique identifier')
    htoken = models.CharField(
        max_length=100, default='Basic XXXXXXXXXXX', help_text='this should be a unique identifier')
    cable_image = models.ImageField(
        default="", help_text="the best image needed here is a square image recommended is 49 x 49px")
    cable_type_price = models.TextField(max_length=13000, default='["|select a DSTV package", "ACSSE36|DStv Access = N2000 + Convinience fee N50|2050|2050", "FTAE36|DStv FTA Plus = N1600 + Convinience fee N50|1650|1650", "COFAME36|DStv Family = N4000 + Convinience fee N50|4050|4050", "ASIAE36|DstvAsiaBouqet = N5400 + Convinience fee N50|5450|5450", "COMPE36|DStv Compact = N6800 + Convinience fee N50|6850|6850", "COMPLE36|DStv Plus = N10650 + Convinience fee N50|10700|10700", "PRWE36|Dstv Premium = N15800 + Convinience fee N50|15850|15850", "DPRHD|DStv Premium Asia Ex= N19900 + Convinience fee N50|19950|19950", "DPRHDP|Dstv Premium Extra = N18000 + Convinience fee N50|18050|18050"]', help_text=mark_safe('<span class="text-danger">["api_code|what_user_sees|api_price|site_price|site_service_code"]</span>'))
    success_code = models.CharField(max_length=500, default='true')
    
    description = models.TextField(default='<h4 id="note"><strong><u>How to Top-Up Airtime</u></strong></h4><p>TOP-UP your MTN, 9MOBILE, AIRTEL, GLO</p><p><li>Choose your Network</li><li>Enter your Recharge Amount</li><li>Enter the Phone number to recharge</li></p><p><strong>The more you recharge, the more bonus point you gathered</strong></p>', help_text="Html is allowed here")

    def __str__(self):
        return self.api_name

    class Meta:
        verbose_name = 'API For Cable Recharge'
        verbose_name_plural = 'APIs For Cable Recharge'
