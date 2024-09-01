from django.urls import path, include
from main import views 
from my_helper import middleware


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('alert_system/', include('alert_system.urls')),
    path('', include('account.urls')), 
    path('flutterwave/', include('flutterwave.urls', namespace='flutterwave')),
    path('paystack/', include('paystack.urls', namespace='paystack')),
    path('strowallet/', include('strowallet.urls')),
    path('transactions/', include('transactions.urls')),
    path('kyc/', include('kyc.urls')),
    path('account/activation/', middleware.simple, name="base")
]
