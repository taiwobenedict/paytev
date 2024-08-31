# paystack/admin.py

from django.contrib import admin
from .models import PaystackConfiguration, PaystackTransaction


class PaystackTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'reference', 'amount', 'paid_at', 'status', 'wallet_before', 'wallet_after'
    )
    search_fields = ('reference', 'user__username')
    list_filter = ('status', 'paid_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'reference', 'amount')
        return self.readonly_fields

admin.site.register(PaystackTransaction, PaystackTransactionAdmin)
admin.site.register(PaystackConfiguration)



