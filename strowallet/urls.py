# strowallet/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_virtual_account, name='create_virtual_account'),
    path('view/', views.view_virtual_account, name='view_virtual_account'),
    path('webhook/', views.webhook, name='webhook'),
]
