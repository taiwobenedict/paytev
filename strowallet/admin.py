from django.contrib import admin
from .models import StrowalletConfig, StrowalletAccount, Hooklog

@admin.register(StrowalletConfig)
class StrowalletConfigAdmin(admin.ModelAdmin):
    list_display = ('public_key', 'secret_key', 'charge_percentage')

@admin.register(StrowalletAccount)
class StrowalletAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'account_name', 'bank_name', 'bank_code', 'customer_email')


@admin.register(Hooklog)
class HooklogAdmin(admin.ModelAdmin):
    list_display = ('myhook',)

