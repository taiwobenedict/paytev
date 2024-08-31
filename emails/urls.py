from django.urls import path
from .views import send_bulk_email

urlpatterns = [
    path('send/', send_bulk_email, name='send_bulk_email'),
]
