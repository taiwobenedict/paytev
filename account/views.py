from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.contrib.auth import authenticate, login as auth_login, get_backends
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db.models import Sum  # Import Sum for aggregation of TotalBalancesView
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout  # To import logout function
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .forms import ResetPinRequestForm, ResetPinTokenForm, ResetPinForm, ProfileForm
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
import random
import string
from datetime import timedelta
from .models import CustomUser, UserOTP
from .forms import RegistrationForm, OTPForm, LoginForm, PasswordResetForm, PasswordResetOTPForm, SetNewPasswordForm
from .models import CreditWalletTransaction, BonusWalletTransaction
import logging

logger = logging.getLogger(__name__)


from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
import string
import logging

logger = logging.getLogger(__name__)

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/registration.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email confirmation
            
            # Initialize wallet credit and bonus balance
            user.wallet_credit = 0.00
            user.bonus_balance = 0.00
            user.pending_balance = 0.00
            
            user.save()  # Save the user instance first to obtain an ID

            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))
            UserOTP.objects.create(user=user, otp=otp, created_at=timezone.now())

            # Send OTP via email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )

            request.session['email'] = user.email  # Store email in session for later use
            return redirect('verify_otp')
        else:
            messages.error(request, 'Please correct the errors below.')
        return render(request, 'account/registration.html', {'form': form})


class OTPVerificationView(View):
    def get(self, request):
        # Display the OTP verification form
        form = OTPForm()
        email = request.session.get('email')  # Retrieve email from session
        return render(request, 'account/enter_otp.html', {'form': form, 'email': email})

    def post(self, request):
        # Process the submitted OTP verification form
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            try:
                user_otp = UserOTP.objects.get(otp=otp, created_at__gte=timezone.now() - timedelta(minutes=10))
                user = user_otp.user
                user.is_active = True # Activate the user's account
                user.save()
                user_otp.delete()  # Remove OTP after successful verification

                # Set the backend attribute on the user object
                backend = get_backends()[0]
                user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
                auth_login(request, user)

                # Send welcome email with template
                self.send_welcome_email(user)

                return redirect('dashboard')
            except UserOTP.DoesNotExist:
                form.add_error('otp', 'Invalid or expired OTP')
        return render(request, 'account/enter_otp.html', {'form': form, 'email': request.session.get('email')})

    def send_welcome_email(self, user):
        subject = 'Welcome to Paytev!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        context = {'user': user}
        
        # Load email template and render with context
        text_content = render_to_string('emails/welcome_email.txt', context)
        html_content = render_to_string('emails/welcome_email.html', context)
        
        # Create and send email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, 'text/html')
        email.send()

    @staticmethod
    def resend_otp(request):
        if request.method == 'POST':
            try:
                email = request.session.get('email')  # Get email from session
                if not email:
                    return JsonResponse({'message': 'Email not found in session'}, status=400)
                
                user = CustomUser.objects.get(email=email)
                user_otp = UserOTP.objects.filter(user=user).first()  # Check if OTP already exists for this user
                if user_otp:
                    # If OTP exists, update the existing OTP instead of creating a new one
                    otp = user_otp.otp
                else:
                    # Generate OTP
                    otp = ''.join(random.choices(string.digits, k=6))
                    UserOTP.objects.create(user=user, otp=otp, created_at=timezone.now())
                
                # Send OTP via email
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                
                return JsonResponse({'message': 'OTP resent successfully!'})
            
            except CustomUser.DoesNotExist:
                return JsonResponse({'message': 'User with this email does not exist'}, status=400)
            
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=400)
        
        return JsonResponse({'message': 'Invalid request'}, status=400)


class PasswordResetView(View):
    def get(self, request):
        form = PasswordResetForm()
        return render(request, 'account/password_reset.html', {'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = CustomUser.objects.get(email=email)
                # Check if there's an existing UserOTP for this user
                user_otp = UserOTP.objects.filter(user=user).first()
                if user_otp:
                    # If OTP already exists, update/send the existing OTP instead of creating a new one
                    otp = user_otp.otp
                else:
                    # Generate OTP
                    otp = ''.join(random.choices(string.digits, k=6))
                    UserOTP.objects.create(user=user, otp=otp, created_at=timezone.now())
                
                # Store email in session
                request.session['email'] = email
                
                # Send OTP via email
                send_mail(
                    'Your OTP Code for Password Reset',
                    f'Your OTP code is {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                
                return redirect('reset_otp')
            
            except CustomUser.DoesNotExist:
                form.add_error('email', 'User with this email does not exist')
            except IntegrityError:
                messages.error(request, 'Failed to create OTP. Please try again later.')
        
        return render(request, 'account/password_reset.html', {'form': form})
    


class PasswordResetOTPView(View):
    def get(self, request):
        # Display the OTP verification form for password reset
        form = PasswordResetOTPForm()
        return render(request, 'account/reset_otp.html', {'form': form})

    def post(self, request):
        # Process the submitted OTP verification form for password reset
        form = PasswordResetOTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            try:
                user_otp = UserOTP.objects.get(otp=otp, created_at__gte=timezone.now() - timedelta(minutes=10))
                # Delete the existing OTP
                user_otp.delete()
                
                # Retrieve user from the OTP object
                user = user_otp.user
                
                # Generate a new OTP
                new_otp = ''.join(random.choices(string.digits, k=6))
                UserOTP.objects.create(user=user, otp=new_otp, created_at=timezone.now())

                # Send the new OTP via email
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {new_otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )

                messages.info(request, 'New OTP sent successfully.')
                return redirect('reset_otp')
            
            except UserOTP.DoesNotExist:
                form.add_error('otp', 'Invalid or expired OTP')
        
        return render(request, 'account/reset_otp.html', {'form': form})


class SetNewPasswordView(View):
    def get(self, request, uidb64):
        # Display the set new password form
        form = SetNewPasswordForm()
        return render(request, 'account/set_new_password.html', {'form': form})

    def post(self, request, uidb64):
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            uid = force_str(urlsafe_base64_decode(uidb64))
            try:
                user = CustomUser.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                return redirect('login')
            except CustomUser.DoesNotExist:
                form.add_error(None, 'Invalid user')
        return render(request, 'account/set_new_password.html', {'form': form})

from django.views import View
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
import string
import logging

logger = logging.getLogger(__name__)

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'account/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                logger.debug(f'User authenticated: {username}, is_active: {user.is_active}')
                if user.is_active:
                    auth_login(request, user)
                    return redirect('dashboard')
                else:
                    logger.debug(f'Resending OTP for inactive user: {username}')
                    try:
                        user_otp = user.userotp  # Attempt to retrieve existing UserOTP object
                        otp = user_otp.otp  # Get the existing OTP
                        send_mail(
                            'Your OTP Code',
                            f'Your OTP code is {otp}',
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                        )
                        messages.info(request, 'Your account is not verified. A new OTP has been sent to your email.')
                        return redirect('verify_otp')  # Redirect to the OTP verification page
                    except UserOTP.DoesNotExist:
                        # Generate a new OTP if UserOTP does not exist (this should not happen in your case)
                        otp = ''.join(random.choices(string.digits, k=6))
                        UserOTP.objects.create(user=user, otp=otp, created_at=timezone.now())
                        send_mail(
                            'Your OTP Code',
                            f'Your OTP code is {otp}',
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                        )
                        messages.info(request, 'Your account is not verified. A new OTP has been sent to your email.')
                        return redirect('verify_otp')  # Redirect to the OTP verification page
            else:
                logger.debug('Invalid username or password')
                messages.error(request, 'Invalid username or password')
        else:
            logger.debug('Form is not valid')
        return render(request, 'account/login.html', {'form': form})


from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import CustomUser, CreditWalletTransaction, BonusWalletTransaction
from alert_system.models import Alert, UserAlertView
from django.http import JsonResponse

class DashboardView(LoginRequiredMixin, View):
    login_url = '/account/login/'  # Redirect to login page if not logged in
    redirect_field_name = 'redirect_to'

    def get(self, request):
        user = request.user
        context = {
            'user': user,
            'show_alert': False,
            'alert_id': None,
            'alert_title': '',
            'alert_message': ''
        }

        # Check for active alerts
        alerts = Alert.objects.filter(is_active=True)
        for alert in alerts:
            # Get or create a UserAlertView instance for the user and the alert
            user_alert_view, created = UserAlertView.objects.get_or_create(user=user, alert=alert)
            if user_alert_view.view_count < alert.view_times:
                # If the alert hasn't been viewed the maximum number of times, show it
                context['show_alert'] = True
                context['alert_id'] = alert.id
                context['alert_title'] = alert.title
                context['alert_message'] = alert.message
                break

        return render(request, 'account/dashboard.html', context)

    def post(self, request):
        user = request.user
        if isinstance(user, CustomUser):
            action = request.POST.get('action')
            if action == 'convert_bonus':
                if user.bonus_balance > 0:
                    # Convert bonus balance to wallet credit
                    user.wallet_credit += user.bonus_balance
                    bonus_amount = user.bonus_balance
                    user.bonus_balance = 0
                    user.save()

                    # Record the transaction
                    CreditWalletTransaction.objects.create(
                        user=user,
                        amount=bonus_amount,
                        transaction_type='credit',
                        description='Converted from Bonus Balance'
                    )
                    BonusWalletTransaction.objects.create(
                        user=user,
                        amount=-bonus_amount,
                        transaction_type='debit',
                        description='Converted to Wallet Credit'
                    )

                    messages.success(request, 'Bonus converted to Wallet Credit successfully!')
                else:
                    messages.error(request, 'No bonus balance to convert.')
            elif action == 'withdraw':
                # Placeholder for withdrawal logic
                pass
            return redirect('dashboard')
        else:
            messages.error(request, 'User data not available')
            return render(request, 'account/dashboard.html')




from django.views import View
from django.http import JsonResponse
from alert_system.models import Alert, UserAlertView

class AcknowledgeAlertView(View):
    def post(self, request):
        try:
            alert_id = request.POST.get('alert_id')
            user = request.user
            
            if alert_id:
                # Retrieve the alert by its ID
                alert = Alert.objects.get(id=alert_id)
                
                # Get or create a UserAlertView instance for the user and the alert
                user_alert_view, created = UserAlertView.objects.get_or_create(user=user, alert=alert)
                
                if user_alert_view.view_count < alert.view_times:
                    # Increment the view count if it hasn't reached the maximum view times
                    user_alert_view.view_count += 1
                    user_alert_view.save()
                    
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Alert view limit reached'})
            
            return JsonResponse({'status': 'error', 'message': 'Alert ID not provided'}, status=400)
        
        except Alert.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Alert not found'})
        
        except Exception as e:
            # Log any other exceptions for debugging purposes
            print(e)
            return JsonResponse({'status': 'error', 'message': 'Error acknowledging alert. Please try again later.'})





        

class CustomLogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('login')  # Redirect to your login URL

    def post(self, request):
        # Handle POST requests if needed
        return self.get(request)  # Redirect as per the GET method
    



class CreditWalletSummaryView(LoginRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        user = request.user
        transactions = CreditWalletTransaction.objects.filter(user=user)
        context = {
            'user': user,
            'transactions': transactions,
        }
        return render(request, 'account/credit_wallet_summary.html', context)

class BonusWalletSummaryView(LoginRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        user = request.user
        transactions = BonusWalletTransaction.objects.filter(user=user)
        context = {
            'user': user,
            'transactions': transactions,
        }
        return render(request, 'account/bonus_wallet_summary.html', context)
    

#Impersonate user view starts from here 
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

class ImpersonateUserListView(ListView):
    model = get_user_model()  # Use the appropriate user model here
    template_name = 'account/impersonate_user_list.html'  # Adjust the template path as needed
    context_object_name = 'users'  # Name used in the template for the queryset

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        # Exclude the current superuser from the list
        return get_user_model().objects.exclude(pk=self.request.user.pk)


from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.backends import ModelBackend  # Import the appropriate backend
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View
from .forms import ImpersonateForm

class ImpersonateUserView(View):
    form_class = ImpersonateForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, user_id):
        user_to_impersonate = get_object_or_404(get_user_model(), pk=user_id)
        
        # Save the current user's ID before logging in as another user
        request.session['impersonator_id'] = request.user.id
        
        # Log in as the target user with a specific authentication backend
        auth_login(request, user_to_impersonate, backend='django.contrib.auth.backends.ModelBackend')
        
        # Redirect to the dashboard or any desired page after impersonation
        return redirect('dashboard')

    def post(self, request, user_id):
        # Handle form submission if needed
        pass




#Admin credit and debit user function 
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AdminWalletActionForm

class AdminWalletActionView(View):
    def get(self, request):
        form = AdminWalletActionForm()
        context = {'form': form}
        return render(request, 'account/admin_wallet_action.html', context)

    def post(self, request):
        form = AdminWalletActionForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            action = form.cleaned_data['action']
            wallet_type = form.cleaned_data['wallet_type']
            amount = form.cleaned_data['amount']
            narration = form.cleaned_data['narration']

            if action == 'credit':
                if wallet_type == 'wallet_credit':
                    user.wallet_credit += amount
                elif wallet_type == 'bonus_balance':
                    user.bonus_balance += amount
            elif action == 'debit':
                if wallet_type == 'wallet_credit':
                    user.wallet_credit -= amount
                elif wallet_type == 'bonus_balance':
                    user.bonus_balance -= amount

            user.save()
            messages.success(request, f'Successfully {action}ed {amount} to {user.username}\'s {wallet_type}. Narration: {narration}')
            return redirect('admin_wallet_action')
        return render(request, 'account/admin_wallet_action.html', {'form': form})



#Implementation of TotalBalancesView 
class TotalBalancesView(View):
    def get(self, request):
        # Calculate the total wallet credit for all users
        total_wallet_credit = CustomUser.objects.aggregate(total_credit=Sum('wallet_credit'))['total_credit'] or 0
        # Calculate the total bonus balance for all users
        total_bonus_balance = CustomUser.objects.aggregate(total_bonus=Sum('bonus_balance'))['total_bonus'] or 0
        # Count the total number of users 
        total_users = CustomUser.objects.count()

        # Now pass the calculated values to the template context
        context = {
            'total_wallet_credit': total_wallet_credit,
            'total_bonus_balance': total_bonus_balance,
            'total_users': total_users,
        }
        # Now render the total balances template with the context
        return render(request, 'account/total_balances.html', context)
    


#Reset PIN views 
User = get_user_model()

def reset_pin_request(request):
    if request.method == 'POST':
        form = ResetPinRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                # Attempt to find a user with the provided email
                user = User.objects.get(email=email)
                # Generate a reset token (consider a more secure method in production)
                reset_token = get_random_string(length=32)
                user.reset_token = reset_token
                user.save()
                # Send an email with the reset token (include a link in a real implementation)
                send_mail(
                    'Reset Your PIN',
                    f'Use this token to reset your PIN: {reset_token}',
                    'test@paytev.com',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Reset token sent to your email')
                return redirect('reset_pin_token')  # Redirect to token entry page
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email')
    else:
        form = ResetPinRequestForm()
    return render(request, 'account/reset_pin_request.html', {'form': form})

def reset_pin_token(request):
    if request.method == 'POST':
        form = ResetPinTokenForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('token')
            user = User.objects.filter(reset_token=token).first()
            if user:
                return redirect('reset_pin_confirm', token=token)  # Redirect to reset pin confirmation page
            else:
                messages.error(request, 'Invalid or expired reset token')
    else:
        form = ResetPinTokenForm()
    return render(request, 'account/reset_pin_token.html', {'form': form})

def reset_pin_confirm(request, token):
    if request.method == 'POST':
        form = ResetPinForm(request.POST)
        if form.is_valid():
            new_pin = form.cleaned_data.get('new_pin')
            user = User.objects.filter(reset_token=token).first()
            if user:
                # Update the user's PIN
                user.pin = new_pin
                user.reset_token = None  # Clear the reset token
                user.save()
                messages.success(request, 'PIN successfully updated')
                return redirect(reverse('dashboard'))  # Redirect to the dashboard with a success message
            else:
                messages.error(request, 'Invalid or expired reset token')
    else:
        form = ResetPinForm()
    return render(request, 'account/reset_pin_confirm.html', {'form': form})



#Profile page views 
@login_required
def view_profile(request):
    user = request.user
    return render(request, 'account/view_profile.html', {'user': user})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'account/edit_profile.html', {'form': form})


def fund_wallet(request):
    return render(request, 'account/fund_wallet.html')

