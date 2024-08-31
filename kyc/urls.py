# kyc/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('kyc/', views.kyc_view, name='kyc_view'),
    path('kyc-success/', views.kyc_success, name='kyc_success'),
    path('form/', views.kyc_view, name='kyc_form'),
    path('success/', views.kyc_success, name='kyc_success'),
    path('status/', views.kyc_status, name='kyc_status'),
    path('admin/', views.kyc_admin_view, name='kyc_admin_view'),
    path('admin/action/<int:kyc_id>/', views.kyc_action, name='kyc_action'),
    
]
