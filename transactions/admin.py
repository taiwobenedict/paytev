from django.contrib import admin
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from .models import Transactions 
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


class TransactionTopupDetailsAdmin(admin.ModelAdmin): 
    list_display = ('user', 'reference', 'bill_type', 'bill_number', 'bill_code', 'actual_amount', 'paid_amount',
                    'old_balance', 'new_balance', 'status', 'bill_provider', 'created_at', 'updated_at', 'api_response')
    list_filter = ('created_at','status', 'bill_type', 'bill_code')
    search_fields = ('user__username', 'bill_type', 'identifier',
                     'status', 'bill_number', 'reference',)
    ordering = ('-created_at',)
    list_per_page = 30
    readonly_fields = ('user', 'email', 'discount', 'customername', 'bill_serial', 'customernumber', 'comment', 'customername', 'phone', 'customer_dt_number', 'api_id', 'mode','amtcredited', 'smsangosbulkcredit', 'callback_url', 'reference', 'bill_type', 'bill_number', 'bill_code', 'actual_amount', 'paid_amount',
                    'old_balance', 'new_balance', 'identifier', 'bill_provider', 'created_at', 'updated_at', 'api_response')

    def has_add_permission(self, request):
        return False  # Disable ability to add new AirtimePurchase entries from admin


    actions = ['refund_selected_transactions']

    """
    def get_queryset(self, request):
        # Filter queryset within the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=90)
        queryset = super().get_queryset(request)
        return queryset.filter(created_at__gte=thirty_days_ago)
    """
"""
    def refund_selected_transactions(self, request, queryset):
        for transaction in queryset:
            try:
                if transaction.status in ["FAILED", "QUEUE", "SUCCESS"]:
                    transaction.status = "REFUNDED"
                    transaction.old_balance = transaction.user.smsbulkcredit.smscredit

                    # Update user's SMS credit balance
                    balance = Wallet.objects.get(
                        user=transaction.user)
                    balance.smscredit += Decimal(transaction.paid_amount)
                    balance.save()

                    # Save the transaction with new balance
                    transaction.new_balance = balance.balance
                    transaction.save()

                    # Compose the email subject and message
                    email_subject = 'Jaratel Just Refunded you!'
                    email_message = (
                        f'Hello {transaction.user.username},\n\n'
                        f'We have successfully refunded your transaction.\n'
                        f'Details of the refunded transaction are as follows:\n\n'
                        f'Phone Number: {transaction.bill_number}\n'
                        f'Plan Code: {transaction.bill_code}\n'
                        f'Refund Amount: #{transaction.paid_amount}\n'
                        f'Transaction Reference: {transaction.reference}\n\n'
                        f'Thank you for using our services.\n'
                        f'Best regards,\n'
                        f'Jaratel Team'
                    )
                    # Assuming the user has an email field
                    recipient_email = transaction.user.email

                    # Send the email
                    send_mail(
                        email_subject,
                        email_message,
                        # Set your default 'from' email address from Django settings
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient_email],
                        # Set to True if you want to suppress exceptions if the email sending fails
                        fail_silently=True,
                    )
            except Exception as e:
                messages.error(
                    request, f'Error refunding transactions: {str(e)}')
                return

        messages.success(request, 'Selected transactions have been refunded.')

    refund_selected_transactions.short_description = 'Refund selected transactions'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('refund_transactions/', self.refund_transactions_view,
                 name='refund_transactions'),
        ]
        return custom_urls + urls

    def refund_transactions_view(self, request):
        selected_ids = request.GET.get('ids')
        if selected_ids:
            queryset = Transactions.objects.filter(
                id__in=selected_ids.split(','))
            self.refund_selected_transactions(request, queryset)
        return HttpResponseRedirect(reverse('admin:transactions_transactiontopupdetails_changelist'))
"""

admin.site.register(Transactions, TransactionTopupDetailsAdmin)
