from django.urls import path
from . import views

app_name = 'flutterwave'

urlpatterns = [
    path('fund/', views.fund_wallet, name='fund_wallet'),
    path('confirm/', views.confirm_funding, name='confirm_funding'),
    path('callback/', views.flutterwave_callback, name='flutterwave_callback'),  # Ensure this path is correct
    path('history/', views.transaction_history, name='transaction_history'),
]
