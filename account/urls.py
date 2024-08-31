from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from .views import AdminWalletActionView
from .views import DashboardView, AcknowledgeAlertView
from . import views
from .views import DashboardView, ImpersonateUserListView, ImpersonateUserView, AdminWalletActionView, TotalBalancesView
from .views import (
    RegistrationView, OTPVerificationView, LoginView, 
    PasswordResetView, PasswordResetOTPView, SetNewPasswordView, 
    DashboardView, CustomLogoutView, CreditWalletSummaryView, BonusWalletSummaryView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='account-dashboard'),
    path('acknowledge-alert/', AcknowledgeAlertView.as_view(), name='acknowledge_alert'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('verify_otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('reset_otp/', PasswordResetOTPView.as_view(), name='reset_otp'),
    path('set_new_password/<uidb64>/', SetNewPasswordView.as_view(), name='set_new_password'),
    path('resend_otp/', OTPVerificationView.resend_otp, name='resend_otp'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),  # Use your custom LogoutView if needed
    path('logout/', LogoutView.as_view(), name='logout'),
    path('credit_wallet_summary/', CreditWalletSummaryView.as_view(), name='credit_wallet_summary'),
    path('bonus_wallet_summary/', BonusWalletSummaryView.as_view(), name='bonus_wallet_summary'),
    path('impersonate-users/', ImpersonateUserListView.as_view(), name='impersonate_user_list'),
    path('impersonate-user/<int:user_id>/', ImpersonateUserView.as_view(), name='impersonate_user'),
    path('admin/wallet/action/', AdminWalletActionView.as_view(), name='admin_wallet_action'),
    path('admin-wallet-action/', AdminWalletActionView.as_view(), name='admin_wallet_action'),
    path('total-balances/', TotalBalancesView.as_view(), name='total_balances'),
    path('reset-pin/', views.reset_pin_request, name='reset_pin_request'),
    path('reset-pin/token/', views.reset_pin_token, name='reset_pin_token'),
    path('reset-pin/confirm/<str:token>/', views.reset_pin_confirm, name='reset_pin_confirm'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('fund-wallet/', views.fund_wallet, name='fund_wallet'),
]