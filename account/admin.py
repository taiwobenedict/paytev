# account/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import CustomUser, CreditWalletTransaction, BonusWalletTransaction


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'wallet_credit', 'bonus_balance', 'is_active', 'is_staff', 'is_superuser', 'view_credit_transactions', 'view_bonus_transactions', 'kyc_status', 'impersonate_link')
    list_filter = ('is_active', 'is_staff', 'kyc_status', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'pin', 'reset_token', 'kyc_status')}),
        ('Balances', {'fields': ('wallet_credit', 'bonus_balance', 'pending_balance')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

    def view_credit_transactions(self, obj):
        url = reverse('admin:account_creditwallettransaction_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">View Credit Transactions</a>', url)
    view_credit_transactions.short_description = 'Credit Transactions'

    def view_bonus_transactions(self, obj):
        url = reverse('admin:account_bonuswallettransaction_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">View Bonus Transactions</a>', url)
    view_bonus_transactions.short_description = 'Bonus Transactions'

    def impersonate_link(self, obj):
        if obj.is_superuser:
            return "-"
        return format_html('<a href="{}">Impersonate</a>', reverse('impersonate_user', args=[obj.id]))
    

    def get_pin(self, obj):
        # Display the PIN in plaintext for admin purposes
        return obj._pin if obj._pin else "Not Set"
    get_pin.short_description = 'PIN'
    

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
