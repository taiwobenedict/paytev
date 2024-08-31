from django.urls import path
from . import views

urlpatterns = [
    path('recharge/', views.recharge_airtime, name='recharge_airtime'),
]
