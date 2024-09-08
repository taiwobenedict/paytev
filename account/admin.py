# account/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import CustomUser, CreditWalletTransaction, BonusWalletTransaction

class CustomUserAdmin(UserAdmin):
    list_display = ("username", "phone_number", "is_active", "is_superuser", "is_staff")
  



admin.site.register(CustomUser, CustomUserAdmin)


class CreditWalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'timestamp'

admin.site.register(CreditWalletTransaction, CreditWalletTransactionAdmin)


class BonusWalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'timestamp'

admin.site.register(BonusWalletTransaction, BonusWalletTransactionAdmin)
