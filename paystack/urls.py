# paystack/urls.py

from django.urls import path
from .views import FundWalletView, InitializePaymentView, VerifyPaymentView, PaymentSuccessView, PaystackWebhookView, transaction_history

app_name = 'paystack'  # Define the namespace for the app

urlpatterns = [
    path('fund-wallet/', FundWalletView.as_view(), name='fund_wallet'),
    path('initialize-payment/', InitializePaymentView.as_view(), name='initialize_payment'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify_payment'),
    path('payment-successful/', PaymentSuccessView.as_view(), name='payment_successful'),
    path('paystack/webhook/', PaystackWebhookView.as_view(), name='paystack_webhook'),
    path('transaction-history/', transaction_history, name='transaction_history'),

]

#https://yourdomain.com/paystack/webhook/
