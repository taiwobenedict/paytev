from django.urls import path
from transactions.views import *
from . import views
from transactions.views import transactions, transactions_details, transaction_list, transactions_failed


app_name = 'transactions'
urlpatterns = [
    path('history/', views.transactions, name='transactions'),
    path('transactions/', transactions, name='list_tranasactions'),
    path('history/', views.transactions, name='transactions'),
    path('history/', transactions, name='list_transactions'),
    path('i/<str:reference>/', transactions_details,
         name='transactions_details_page'),
    path('bill/<str:reference>/', transactions_failed,
         name='transactions_details_failed'),
    path('api/transaction-list/', transaction_list, name='transaction_list'),
]