import uuid
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Transaction

@login_required
def fund_wallet(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        flutterwave_charge = calculate_flutterwave_charge(amount)  # Calculate charge
        total_amount = float(amount) + flutterwave_charge
        request.session['fund_amount'] = amount
        request.session['total_amount'] = total_amount
        return redirect(reverse('flutterwave:confirm_funding'))  # Redirect using namespaced URL
    return render(request, 'flutterwave/fund_wallet.html')

def generate_tx_ref(user_id):
    return f'tx_{user_id}_{uuid.uuid4()}'

@login_required
def confirm_funding(request):
    # Display confirmation page with amount and charges
    amount = request.session.get('fund_amount')
    total_amount = request.session.get('total_amount')
    flutterwave_charge = total_amount - float(amount)

    if request.method == 'POST':
        print("POST request received")  # Debugging line
        print(f"Session Data: Amount - {amount}, Total Amount - {total_amount}")  # Debugging line

        headers = {
            'Authorization': f'Bearer: {settings.FLUTTERWAVE_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        # Generate unique transaction reference
        tx_ref = generate_tx_ref(request.user.id)

        payload = {
            'tx_ref': tx_ref,
            'amount': total_amount,
            'currency': 'NGN',
            'redirect_url': request.build_absolute_uri(reverse('flutterwave:flutterwave_callback')),
            'customer': {
                'email': request.user.email,
                'phonenumber': request.user.phone_number,  # Assuming phone number is in user profile
                'name': request.user.get_full_name()
            },
            'customizations': {
                'title': 'Fund Wallet',
                'description': 'Wallet Funding'
            }
        }

        print("Headers:", headers)  # Debugging line
        print("Payload:", payload)  # Debugging line

        response = requests.post('https://api.flutterwave.com/v3/payments', json=payload, headers=headers)

        try:
            data = response.json()
            print("Response data:", data)  # Debugging line
        except ValueError:
            print("Failed to decode JSON response")  # Debugging line
            print("Response content:", response.content)  # Debugging line
            return render(request, 'flutterwave/payment_failed.html', {'message': 'Invalid response from payment gateway'})

        if data['status'] == 'success':
            payment_url = data['data']['link']
            return redirect(payment_url)
        else:
            return render(request, 'flutterwave/payment_failed.html', {'message': data['message']})

    return render(request, 'flutterwave/confirm_funding.html', {
        'amount': amount,
        'total_amount': total_amount,
        'flutterwave_charge': flutterwave_charge,
    })

@login_required
def flutterwave_callback(request):
    # Handle Flutterwave payment callback
    status = request.GET.get('status')
    tx_ref = request.GET.get('tx_ref')
    transaction_id = request.GET.get('transaction_id')

    if status == 'successful':
        headers = {'Authorization': f'Bearer: {settings.FLUTTERWAVE_SECRET_KEY}'}
        response = requests.get(
            f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify', headers=headers)
        data = response.json()
        if data['status'] == 'success':
            amount = data['data']['amount']
            user = request.user
            user.wallet_credit += amount  # Adjust wallet credit
            user.save()
            Transaction.objects.create(
                user=user,
                amount=amount,
                reference=tx_ref,
                status='successful'
            )
            return render(request, 'flutterwave/payment_successful.html', {
                'amount': amount,
                'reference': tx_ref,
                'amount_before': user.wallet_credit - amount,
                'amount_after': user.wallet_credit,
                'status': 'successful',
            })
    return render(request, 'flutterwave/payment_failed.html')

@login_required
def transaction_history(request):
    # Display user's transaction history
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'flutterwave/transaction_history.html', {'transactions': transactions})

# Utility function to calculate Flutterwave charge
def calculate_flutterwave_charge(amount):
    # Example calculation; replace with actual Flutterwave charge logic
    return float(amount) * 0.015  # 1.5% charge
