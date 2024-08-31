# paystack/views.py

import json
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from .models import PaystackTransaction, PaystackConfiguration
from account.models import CustomUser
from .forms import FundWalletForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from decimal import Decimal

def get_paystack_configuration():
    config = PaystackConfiguration.objects.first()
    if config:
        return {
            'public_key': config.public_key,
            'secret_key': config.secret_key,
            'paystack_charge': config.paystack_charge
        }
    return None

from decimal import Decimal

class FundWalletView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = FundWalletForm()
        return render(request, 'paystack/fund_wallet.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = FundWalletForm(request.POST)
        if form.is_valid():
            amount = Decimal(form.cleaned_data['amount'])
            config = get_paystack_configuration()
            if not config:
                return render(request, 'paystack/error.html', {'error': 'Paystack configuration not found.'})

            paystack_charge_percentage = Decimal(config['paystack_charge'])
            paystack_charge = amount * paystack_charge_percentage
            total_amount = amount + paystack_charge

            request.session['amount'] = str(amount)
            request.session['total_amount'] = str(total_amount)
            return render(request, 'paystack/confirm_funding.html', {
                'amount': amount,
                'paystack_charge': paystack_charge,
                'total_amount': total_amount
            })
        return render(request, 'paystack/fund_wallet.html', {'form': form})


class InitializePaymentView(View):
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        user = request.user
        total_amount = Decimal(request.session.get('total_amount'))
        config = get_paystack_configuration()
        if not config:
            return JsonResponse({'error': 'Paystack configuration not found.'}, status=400)
            
        headers = {
            'Authorization': f'Bearer {config["secret_key"]}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': user.email,
            'amount': int(total_amount * 100),
            'callback_url': request.build_absolute_uri('/paystack/verify-payment/'),
        }
        response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
        
        # Debug print for API response
        print("Initialize Payment Response: ", response.json())
        
        response_data = response.json()
        
        if response_data['status']:
            PaystackTransaction.objects.create(
                user=user,
                reference=response_data['data']['reference'],
                amount=total_amount
            )
            return JsonResponse({'payment_url': response_data['data']['authorization_url']})
        else:
            return JsonResponse({'error': response_data['message']}, status=400)

class VerifyPaymentView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        reference = request.GET.get('reference')
        config = get_paystack_configuration()
        if not config:
            return render(request, 'paystack/error.html', {'error': 'Paystack configuration not found.'})

        headers = {
            'Authorization': f'Bearer {config["secret_key"]}',
            'Content-Type': 'application/json',
        }
        response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
        response_data = response.json()

        if response_data['status'] and response_data['data']['status'] == 'success':
            transaction = PaystackTransaction.objects.get(reference=reference)
            if not transaction.verified:
                transaction.verified = True
                transaction.paid_at = response_data['data']['paid_at']
                transaction.status = 'success'
                
                user = request.user
                amount = Decimal(request.session.get('amount'))
                previous_wallet_credit = user.wallet_credit
                user.wallet_credit += amount
                user.save()

                transaction.wallet_before = previous_wallet_credit
                transaction.wallet_after = user.wallet_credit
                transaction.save()

                return render(request, 'paystack/payment_successful.html', {
                    'transaction_reference': transaction.reference,
                    'transaction_date': transaction.paid_at,
                    'funded_amount': amount,
                    'amount_before': transaction.wallet_before,
                    'amount_after': transaction.wallet_after,
                    'status': transaction.status
                })
            else:
                return render(request, 'paystack/payment_successful.html', {
                    'transaction_reference': transaction.reference,
                    'transaction_date': transaction.paid_at,
                    'funded_amount': transaction.amount,
                    'amount_before': transaction.wallet_before,
                    'amount_after': transaction.wallet_after,
                    'status': transaction.status
                })
        else:
            return render(request, 'paystack/payment_failed.html', {
                'error': response_data['message']
            })


class PaymentSuccessView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        amount = request.session.get('amount')
        wallet_credit = request.user.wallet_credit
        return render(request, 'paystack/payment_successful.html', {
            'amount': amount,
            'wallet_credit': wallet_credit
        })

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import PaystackTransaction
from decimal import Decimal

@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(View):
    def post(self, request, *args, **kwargs):
        event = json.loads(request.body)
        
        # Debug print for webhook event
        print("Webhook Event: ", event)

        if event['event'] == 'charge.success':
            reference = event['data']['reference']
            amount = Decimal(event['data']['amount']) / 100  # Convert kobo to naira
            status = event['data']['status']
            paid_at = event['data']['paid_at']

            try:
                transaction = PaystackTransaction.objects.get(reference=reference)
                if not transaction.verified:
                    user = transaction.user
                    user.wallet_credit += amount
                    user.save()
                    
                    transaction.status = status
                    transaction.paid_at = paid_at
                    transaction.verified = True
                    transaction.save()
                    
                    return JsonResponse({'status': 'success'}, status=200)
                else:
                    return JsonResponse({'status': 'already_verified'}, status=200)
            except PaystackTransaction.DoesNotExist:
                return JsonResponse({'error': 'Transaction not found'}, status=404)

        return JsonResponse({'status': 'invalid_event'}, status=400)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import PaystackTransaction

@login_required
def transaction_history(request):
    user = request.user
    search_query = request.GET.get('search', '')

    # Base query for transactions
    transactions = PaystackTransaction.objects.filter(user=user)
    
    # Apply search filter if search_query is provided
    if search_query:
        transactions = transactions.filter(
            Q(reference__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(amount__icontains=search_query)
        )
    
    # Order transactions by date descending
    transactions = transactions.order_by('-paid_at')
    
    # Paginate transactions
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'paystack/transaction_history.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })
