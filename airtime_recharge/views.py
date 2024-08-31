import json
import requests
import random
import string
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AirtimeRechargeForm
from .models import AirtimePurchase, AirtimeAPIConfiguration
from .serializers import HusmoDataAPISerializer

def generate_request_id():
    return 'PAYTEV' + ''.join(random.choices(string.ascii_uppercase, k=4)) + ''.join(random.choices(string.digits, k=4))

@login_required
def recharge_airtime(request):
    if request.method == 'POST':
        form = AirtimeRechargeForm(request.POST)
        if form.is_valid():
            airtime_purchase = form.save(commit=False)
            airtime_purchase.user = request.user

            request_id = generate_request_id()
            airtime_purchase.request_id = request_id

            if request.user.wallet_credit >= airtime_purchase.amount:
                airtime_purchase.old_balance = request.user.wallet_credit
                amount_float = float(airtime_purchase.amount)
                api_config = AirtimeAPIConfiguration.objects.filter(is_active=True).first()

                if api_config:
                    api_data = api_config.api_data.copy()

                    if api_config.api_name == 'VTPass':
                        api_data['data']['serviceID'] = form.cleaned_data['network_provider']
                        api_data['data']['amount'] = amount_float
                        api_data['data']['phone'] = form.cleaned_data['phone_number']
                        api_data['data']['request_id'] = request_id

                        headers = api_data['headers']
                        headers['Content-Type'] = 'application/json'  # Ensure Content-Type is set
                        url = api_config.api_url

                        try:
                            response = requests.post(url, json=api_data['data'], headers=headers)
                            response_data = response.json()

                            if response.status_code == 200 and response_data.get('code') == api_config.success_code:
                                airtime_purchase.new_balance = request.user.wallet_credit - airtime_purchase.amount
                                airtime_purchase.reference_number = response_data.get('requestId', '')
                                airtime_purchase.api_response = json.dumps(response_data)
                                airtime_purchase.status = 'completed'
                                airtime_purchase.save()

                                request.user.wallet_credit -= airtime_purchase.amount
                                request.user.save()

                                messages.success(request, 'Airtime purchase successful!')
                                return redirect('dashboard')

                            else:
                                airtime_purchase.api_response = json.dumps(response_data)
                                airtime_purchase.status = 'failed'
                                airtime_purchase.save()
                                messages.error(request, f'Failed to purchase airtime: {response_data.get("response_description", "Unknown error")}')

                        except requests.exceptions.RequestException as e:
                            airtime_purchase.api_response = str(e)
                            airtime_purchase.status = 'failed'
                            airtime_purchase.save()
                            messages.error(request, f'Failed to connect to API: {e}')

                    elif api_config.api_name == 'HusmoDataAPI':
                        husmo_data = {
                            'network': form.cleaned_data['network_provider'],
                            'amount': amount_float,
                            'mobile_number': form.cleaned_data['phone_number'],
                            'airtime_type': 'VTU',
                            'Ported_number': 'false'
                        }

                        # Use serializer to validate and format data
                        serializer = HusmoDataAPISerializer(data=husmo_data)
                        if serializer.is_valid():
                            headers = api_data['headers']
                            headers['Content-Type'] = 'application/json'  # Ensure Content-Type is set
                            url = api_config.api_url

                            try:
                                response = requests.post(url, data=json.dumps(serializer.validated_data), headers=headers)
                                print(f"Raw Response Text from HusmoDataAPI: {response.text}")  # Debugging
                                response_data = response.json()

                                print(f"Parsed Response Data from HusmoDataAPI: {response_data}")  # Debugging

                                if response.status_code == 200 and 'error' not in response_data:
                                    airtime_purchase.new_balance = request.user.wallet_credit - airtime_purchase.amount
                                    airtime_purchase.reference_number = response_data.get('requestId', '')
                                    airtime_purchase.api_response = json.dumps(response_data)
                                    airtime_purchase.status = 'completed'
                                    airtime_purchase.save()

                                    request.user.wallet_credit -= airtime_purchase.amount
                                    request.user.save()

                                    messages.success(request, 'Airtime purchase successful!')
                                    return redirect('dashboard')

                                else:
                                    airtime_purchase.api_response = json.dumps(response_data)
                                    airtime_purchase.status = 'failed'
                                    airtime_purchase.save()
                                    messages.error(request, f'Failed to purchase airtime: {response_data.get("error", "Unknown error")}')

                            except requests.exceptions.RequestException as e:
                                airtime_purchase.api_response = str(e)
                                airtime_purchase.status = 'failed'
                                airtime_purchase.save()
                                messages.error(request, f'Failed to connect to API: {e}')
                        else:
                            messages.error(request, f'Serializer error: {serializer.errors}')

                else:
                    messages.error(request, 'No active API configuration found.')
            else:
                messages.error(request, 'Insufficient wallet balance.')
    else:
        form = AirtimeRechargeForm()

    return render(request, 'airtime_recharge/recharge_airtime.html', {'form': form})
