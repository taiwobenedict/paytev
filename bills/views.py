#bills views.py

from django.shortcuts import render
import uuid
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control, never_cache
import requests
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.validators import RegexValidator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View, generic
from django.views.generic import CreateView, DetailView, ListView, \
    TemplateView
import datetime
import random
import re
from re import template
import json
from django.contrib.auth.models import User
from bills.models import CableRecharegAPI, DataNetworks, RechargeAirtimeAPI
from bills.utility import get_or_none
from transactions.models import Transactions
from account.models import CustomUserManager, CustomUser
from decimal import *
from my_helper.helpers import evalResponse, deleteSessions, setSessions, timezoneshit
#from my_helper import prevent_double
import ast
from django.db.models import Sum
from django.db import transaction
from transactions.models import Transactions
from kyc.models import KYCSettings 
import logging

logger = logging.getLogger(__name__)

def general_logic(request):
    # Render a template named 'general.html' 
    return render(request, 'bills/general.html')

def buynow(request):
    # Render a template named 'general.html' 
    return render(request, 'bills/buy.html')

UserModel = get_user_model() 

@login_required(login_url=settings.LOGIN_URL)
def AirtimeEmptyTemplate(request):
  user = request.user

  template_name = "bills/general.html"
  api_obj = RechargeAirtimeAPI.objects.filter(is_active=True)
  return render(request, template_name, {'products': api_obj, 'title': "Airtime", 'link': '/bills/go'})

@login_required(login_url=settings.LOGIN_URL)
def AirtimeProcessTemplate(request, code):
  template_name = "bills/buyairtime.html"
  obj = RechargeAirtimeAPI.objects.filter(is_active=True, identifier=code)
  if len(obj) > 0:
    return render(request, template_name, {'code': code, 'obj': obj[0]})
  messages.success(
      request, "Sorry, error. Seems you used the wrong link")
  return redirect(reverse('bills:general'))

@login_required(login_url=settings.LOGIN_URL)
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def AirtimeView(request):

    user = request.user

    # Fetch the transaction limit from KYC settings
    kyc_settings = KYCSettings.objects.first()
    TRANSACTION_LIMIT = kyc_settings.transaction_limit if kyc_settings else 0

    if request.method == "POST":
        # Generate a unique token
        unique_token = str(uuid.uuid4())

        # Check if the form has already been processed
        if request.session.get(unique_token, False):
            # Handle the duplicate submission (e.g., show an error message)
            messages.error(
                request, 'Duplicate submission detected. Please check your transaction history. Or you try again shortly')
            return redirect(reverse('bills:general'))

        # Store the unique token in the session
        request.session[unique_token] = True

        # Check if the user is unverified
        if user.kyc.status in ['Not Verified', 'Submitted', 'Rejected']:
            # Get the time 24 hours ago
            time_limit = timezone.now() - timedelta(days=1)

            # Query transactions in the last 24 hours for this user
            recent_transactions = Transactions.objects.filter(
                user=user,
                created_at__gte=time_limit
            )

            # Calculate the total amount spent
            total_recent_amount = recent_transactions.aggregate(total=Sum('paid_amount'))['total'] or 0

            # Log the total recent amount
            logger.debug(f"Total amount spent by user {user.username} in the past 24 hours: {total_recent_amount}")

            # Check if the user has exceeded the limit
            if total_recent_amount >= TRANSACTION_LIMIT:
                # Remove the unique token from the session before returning
                del request.session[unique_token]

                messages.error(request, "Daily transaction limit exceeded. Verify your account now")
                return redirect(reverse('bills:general'))


        # Process the form data
        network = request.POST.get('network')
        code = request.POST.get('code')
        phone = (request.POST.get('phone')).strip()
        our_provider = str(request.POST.get('providers'))
        amt = request.POST.get('amt')
        amt = float(amt)
        amt = abs(int(amt))
        pin = request.POST.get('pin').strip()
        phone = phone.replace(" ", "")
        smsbal = user.wallet_credit

        if float(amt) > float(smsbal) or int(smsbal) <= 0 or float(amt) <= 0:
            # Remove the unique token from the session before returning
            del request.session[unique_token]

            messages.error(request, "Insufficient fund")
            return redirect(reverse('bills:general'))
            
 # Validate PIN
        if not user.pin or user.pin != pin:
        #Remove the unique token from the session if PIN is invalid
            request.session.pop(unique_token)  # Using pop() to avoid KeyError
            messages.error(request, "Invalid PIN.")
            return redirect(reverse('bills:general'))



        if float(amt) < 5:
            # Remove the unique token from the session before returning
            del request.session[unique_token]

            messages.error(request, "Failed: Amount must be N50 above!")
            return redirect(reverse('bills:general'))

        if len(phone) != 11:
            # Remove the unique token from the session before returning
            del request.session[unique_token]

            messages.error(request, "Failed: Phone number must be 11 digits!")
            return redirect(reverse('bills:general'))

        api_obj = get_or_none(RechargeAirtimeAPI,
                              is_active=True, identifier=code)
        if api_obj is None:
            messages.error(request, "Please retry")
            return redirect(reverse('bills:general'))

        old_balance = smsbal
        get_amt = float(amt) - (float(amt) * float(api_obj.user_discount))

        # Deduct the amount from the user's wallet
        user.wallet_credit -= Decimal(float(get_amt))
        user.save()


        # Try to process the airtime purchase
        try:
            response = process_airtime_purchase(
                api_obj, user, phone, amt, get_amt)
            api_response = response['response']
            if response['status'] == 'SUCCESS':
                status = 'SUCCESS'
            else:
                status = 'FAILED'
                # Refund the user if the transaction failed
                user.wallet_credit -= Decimal(float(get_amt))
                user.save()

        except Exception as e:
            status = 'QUEUE'
            api_response = str(e)
            

        # Create the transaction record 
        obj = Transactions.objects.create(
            user=user,
            bill_type="AIRTIME",
            bill_code=code,
            bill_number=phone,
            bill_provider=our_provider,
            identifier=code,
            actual_amount=amt,
            paid_amount=get_amt if status == 'SUCCESS' else 0.0,
            old_balance=old_balance,
            new_balance=user.wallet_credit,
            status=status,
            reference=timezoneshit(),
            api_id=api_obj.id,
            email=user.email,
            mode="DIRECT",
            api_response=api_response
        )

        # Remove the unique token from the session after processing
        del request.session[unique_token]

        if status == 'SUCCESS':
            messages.success(request, "Airtime purchase successful")
            return HttpResponseRedirect(f'/transactions/i/{obj.reference}/')
        else:
            messages.error(request, "Airtime purchase failed")
            return HttpResponseRedirect(f'/transactions/i/{obj.reference}/')

        return redirect(reverse('bills:general'))

    else:
        messages.error(request, "Failed")
        return redirect(reverse('bills:general'))


def process_airtime_purchase(api_obj, user, phone, amt, get_amt):
    # This function handles the actual airtime purchase logic
    getApiUrl = api_obj.api_url
    getApiUrlData = api_obj.api_url_data

    replace_keys = (('[phone]', phone), ('[amt]', str(amt)), ('[ordernumber]', timezoneshit()),
                    ('[PHONE]', phone), ('[AMT]', str(amt)), ('[ORDERNUMBER]', timezoneshit()))

    for (i, j) in replace_keys:
        getApiUrl = getApiUrl.replace(i, j)
        getApiUrlData = str(getApiUrlData).replace(i, j)

    paramet = ast.literal_eval(getApiUrlData)

    from my_helper import request_method
    response = request_method.call_external_api(
        getApiUrl, paramet['data'], paramet['headers'])

    if any(respo in str(response) for respo in api_obj.success_code.split(",")):
        return {'status': 'SUCCESS', 'response': response}
    else:
        return {'status': 'FAILED', 'response': response}







############
#DATA

@login_required(login_url=settings.LOGIN_URL)
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def Godata(request):
    user = request.user

    template_name = "bills/general.html"
    api_obj = DataNetworks.objects.filter(is_active=True)
    return render(request, template_name, {'products': api_obj, 'title': "Buy Data", 'link': '/bills/m'})

@login_required(login_url=settings.LOGIN_URL)
def DataProcessTemplate(request, code):
    template_name = "bills/buydata.html"
    obj = DataNetworks.objects.filter(is_active=True, identifier=code)
    items = []

    if len(obj) > 0:
        toJson = obj[0].network_data_amount_json.split(',')
        print(toJson)

        for i in toJson:
            print(i)
            item = {}
            x = i.split('|')

            item['api_amount'] = x[0]
            item['data_amount'] = x[1]
            item['urlvariable'] = x[2]
            item['what_user_sees'] = x[3]

            try:
                item['extra_variable'] = x[4]
            except:
                pass

            items.append(item)

        return render(request, template_name, {'code': code, 'obj': obj[0], 'items': items})

    messages.success(
        request, "Sorry, Error!")
    return redirect(reverse('bills:general'))
    return render(request, template_name, {'code': code, 'obj': obj, 'items': items})


@login_required(login_url=settings.LOGIN_URL)
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
#@transaction.atomic
def DataTopUpView(request):
    user = request.user

    if request.method == "POST":
        unique_token = str(uuid.uuid4())

        if request.session.get(unique_token, False):
            messages.error(
                request, 'Duplicate submission detected. Please check your transaction history.')
            return redirect(reverse('bills:general'))

        request.session[unique_token] = True

        data_network = request.POST.get('network')
        code = request.POST.get('code')
        data_number = (request.POST.get('phone')).strip()
        data_size = request.POST.get('amt')
        our_provider = str(request.POST.get('providers'))
        pin = request.POST.get('pin').strip()
        smsbal = user.wallet_credit

        split_amt = data_size.strip().split('|')
        api_amt_plan = split_amt[0]
        data_amount = split_amt[1]
        url_variable = split_amt[2]  # This will be passed to processmypurchase

        old_balance = user.wallet_credit

        dataapi = get_or_none(DataNetworks, is_active=True, identifier=code)

        if dataapi is None:
            messages.error(request, "Data network not found or inactive.")
            return redirect(reverse('bills:general'))

        if data_size not in dataapi.network_data_amount_json:
            messages.error(request, "Fraud detected")
            return redirect(reverse('bills:general'))

        if float(data_amount) > float(user.wallet_credit) or int(user.wallet_credit) <= 0 or float(data_amount) <= 0:
            del request.session[unique_token]
            messages.error(request, "Insufficient fund")
            return redirect(reverse('bills:general'))

        if not user.pin or user.pin != pin:
            del request.session[unique_token]
            messages.error(request, "Invalid PIN.")
            return redirect(reverse('bills:general'))

        if len(data_number) != 11:
            del request.session[unique_token]
            messages.error(request, "Failed: Phone number must be 11 digits!")
            return redirect(reverse('bills:general'))
        
        #percentage = dataapi.referrer_bonus
        
        #time.sleep(random.uniform(1, 3))
        #if user.agent==True:
         #   data_amount = float(data_amount) - (float(data_amount) *
          #                              float(dataapi.agent_discount))

# Deduct the amount from the user's wallet
        user.wallet_credit -= Decimal(float(data_amount))
        user.save()
        
        # Check for recent successful transaction
        myplan_code = data_size.strip().split('|')[2]
        recent_transactions = Transactions.objects.filter(
            user=user,
            bill_number=data_number,
            bill_code=myplan_code,
            status='SUCCESS'
        ).order_by('-created_at')

        if recent_transactions.exists():
            last_transaction = recent_transactions.first()
            time_difference = timezone.now() - last_transaction.created_at

            if time_difference < timedelta(seconds=20):
                del request.session[unique_token]
                messages.error(
                    request, "Please wait a minute before making another transaction.")
                return redirect(reverse('bills:general'))

        try:
            response = processmypurchase(
                dataapi, user, data_number, split_amt, api_amt_plan, url_variable)
            api_response = response['response']
            if response['status'] == 'SUCCESS':
                status = 'SUCCESS'
            else:
                status = 'FAILED'
                user.wallet_credit += Decimal(float(data_amount))
                user.save()

        except Exception as e:
            status = 'QUEUE'
            api_response = str(e)
        plan_code = data_size.strip().split('|')[2]
        obj = Transactions.objects.create(
            user=user,
            bill_type="DATA",
            bill_code=plan_code,
            bill_number=data_number,
            bill_provider=our_provider,
            identifier=code,
            actual_amount=data_amount,
            old_balance=old_balance,
            new_balance=user.wallet_credit,
            reference=timezoneshit(),
            paid_amount=data_amount if status == 'SUCCESS' else 0.0,
            status=status,
            api_id=dataapi.id,
            email=user.email,
            api_response=api_response,
            mode="DIRECT"
        )

        del request.session[unique_token]

        if status == 'SUCCESS':
            #credit_referrer_bonus(user, data_amount, percentage)
            
            return HttpResponseRedirect(f'/transactions/i/{obj.reference}/')
        else:
            
            return HttpResponseRedirect(f'/transactions/i/{obj.reference}/')

        return redirect(reverse('bills:general'))

    else:
        messages.error(request, "Failed")
        return redirect(reverse('bills:general'))


def processmypurchase(dataapi, user, data_number, split_amt, api_amt_plan, url_variable):
    getApiUrl = dataapi.api_url
    getApiUrlData = dataapi.api_url_data
    replace_keys = (
        ('[phone]', data_number),
        ('[dataplan]', api_amt_plan),
        ('[apiamount]', api_amt_plan),
        ('[urlvariable]', url_variable),
        ('[ordernumber]', timezoneshit()),
        ('[PHONE]', data_number),
        ('[DATAPLAN]', api_amt_plan),
        ('[APIAMOUNT]', api_amt_plan),
        ('[URLVARIABLE]', url_variable),
        ('[ORDERNUMBER]', timezoneshit()),
        #('[EXTRAVARIABLE]', extra_variable),
        #('[extravariable]', extra_variable)
    )

    for (i, j) in replace_keys:
        getApiUrl = getApiUrl.replace(i, j)
        getApiUrlData = str(getApiUrlData).replace(i, j)

    paramet = ast.literal_eval(getApiUrlData)
    from my_helper import request_method
    response = request_method.call_external_api(
        getApiUrl, paramet['data'], paramet['headers'])

    if any(respo in str(response) for respo in dataapi.success_code.split(",")):
        return {'status': 'SUCCESS', 'response': response}
    else:
        return {'status': 'FAILED', 'response': response}
    

    ###########################
#Cable########



@login_required(login_url=settings.LOGIN_URL)
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def Givemecable(request):
    user = request.user

    template_name = "bills/general.html"
    api_obj = CableRecharegAPI.objects.filter(is_active=True)
    return render(request, template_name, {'products': api_obj, 'title': "Cable TV", 'link': '/bills/cable'})


@login_required(login_url=settings.LOGIN_URL)
def CableProcessTemplate(request, code):
    template_name = "bills/iuc_form.html"
    obj = CableRecharegAPI.objects.filter(is_active=True, identifier=code)
    items = []

    if len(obj) > 0:
        toJson = obj[0].cable_type_price.split(',')
        print(toJson)

        for i in toJson:
            print(i)
            item = {}
            x = i.split('|')

            item['api_amount'] = x[0]
            item['data_amount'] = x[1]
            item['urlvariable'] = x[2]
            item['what_user_sees'] = x[3]

            try:
                item['extra_variable'] = x[4]
            except:
                pass

            items.append(item)

        return render(request, template_name, {'code': code, 'obj': obj[0], 'items': items})

    messages.success(
        request, "Sorry, Error!")
    return redirect(reverse('topup:general'))
    return render(request, template_name, {'code': code, 'obj': obj, 'items': items})


def iuc_view(request):
    if request.method == 'POST':
        network = request.POST.get('network')
        
        code = request.POST.get('code')
        amt = request.POST.get('amt')
        iuc = request.POST.get('iuc')
        phone = request.POST.get('phone')
        cableapi = get_or_none(CableRecharegAPI, is_active=True, identifier=code)
        api = cableapi.vtoken
        providers = cableapi.provider
        
        
        split_amt = amt.strip().split('|')
        plan_code = split_amt[0]
        amount = split_amt[1]
        plan = split_amt[2]

        # Define the URL and headers
        url = "https://vtpass.com/api/merchant-verify"
        headers = {
            # Replace with your actual API key
            "Authorization": api,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Define the payload data
        payload = {
            'serviceID': code,
            'billersCode': iuc
        }

        try:
            # Make a POST request with headers and payload
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Print raw response text for debugging
            print("Raw response text:", response.text)

            # Parse JSON response
            result = response.json()
            print("Parsed result:", result)

            if result.get('code') == '000':
                customer_name = result.get('content', {}).get(
                    'Customer_Name', 'Unknown')
                context = {
                    'network': network,
                    'providers': providers,
                    'code': code,
                    'amt': plan_code,
                    'phone': phone,
                    'iuc': iuc,
                    'amount': amount,
                    'customer_name': customer_name,
                }
                return render(request, 'bills/topup_form.html', context)
            else:
                messages.error(request, f"Invalid IUC number. API response code: {
                               result.get('code')}")
                return redirect('bills:iuc')

        except requests.RequestException as e:
            error_message = f"API request error: {e}"
            print(error_message)
            messages.error(request, error_message)
            return redirect('bills:iuc')

        except ValueError as e:
            error_message = f"JSON parsing error: {e}"
            print(error_message)
            messages.error(request, error_message)
            return redirect('bills:iuc')

    return render(request, 'bills/iuc_form.html')




def process_topup(request):
    user = request.user
    if request.method == 'POST':
        unique_token = str(uuid.uuid4())

        if request.session.get(unique_token, False):
            messages.error(
                request, 'Duplicate submission detected. Please check your transaction history.')
            return redirect(reverse('topup:general'))

        request.session[unique_token] = True
        
        
        code = request.POST['code']
        plan = request.POST['plan']
        iuc = request.POST['iuc']
        phone = request.POST['phone']
        pin = request.POST.get('pin').strip()
        amount = request.POST['amount']
        
        
        
        
        cableapi = get_or_none(
            CableRecharegAPI, is_active=True, identifier=code)
        api = cableapi.vtoken
        provider = cableapi.provider
        smsbal = user.wallet_credit
        
        old_balance = user.wallet_credit
        
        # Validate PIN
        if not user.pin or user.pin != pin:
            del request.session[unique_token]
            messages.error(request, "Invalid PIN.")
            return redirect(reverse('bills:general'))

        
        if float(amount) > float(user.wallet_credit) or int(user.wallet_credit) <= 0 or float(amount) <= 0:
            # Remove the unique token from the session before returning
            del request.session[unique_token]

            messages.error(request, "Insufficient funds")
            return redirect(reverse('topup:general'))
        
        #percentage = cableapi.referrer_bonus

        # time.sleep(random.uniform(1, 3))
        #if user.agent == True:
            #amount = float(amount) - (float(amount) *
                                              #  float(cableapi.agent_discount))
        
        user.wallet_credit -= Decimal(float(amount))
        user.save()
        
        ref = timezoneshit()
        
        try:
            response = processcable(
                cableapi, user, phone, amount, code, iuc, plan, ref)
            api_response = response
            if response['status'] == 'SUCCESS':
                #credit_referrer_bonus(user, amount, percentage)
                status = 'SUCCESS'
            else:
                status = 'FAILED'
                user.wallet_credit += Decimal(float(amount))
                user.save()

        except Exception as e:
            status = 'QUEUE'
            api_response = str(e)
        
        obj = Transactions.objects.create(
            user=user,
            bill_type="CABLE",
            bill_code=plan,
            bill_number=iuc,
            bill_provider=provider,
            identifier=code,
            actual_amount=amount,
            old_balance=old_balance,
            new_balance=user.wallet_credit,
            reference=ref,
            paid_amount=amount if status == 'SUCCESS' else 0.0,
            status=status,
            api_id=cableapi.id,
            email=user.email,
            api_response=api_response,
            mode="DIRECT"
        )

        del request.session[unique_token]

        if status == 'SUCCESS':
            #credit_referrer_bonus(user, data_amount, percentage)
            
            return HttpResponseRedirect(f'/transactions/i/{obj.reference}/')
        else:
            
            return HttpResponseRedirect(f'/transactions/i/{obj.reference}/')

        return redirect(reverse('bills:general'))

    else:
        messages.error(request, "Failed")
        return redirect(reverse('bills:general'))


def processcable(cableapi, user, phone, amount, code, iuc, plan, ref):
    Url = cableapi.api_url
    
    replace_keys = (
        ('[SMART_NO]', iuc),
        ('[PLAN_AMOUNT]', amount),
        ('[PHONE]', phone),
        ('[ORDER_NUMBER]', ref),
        ('[PLAN_CODE]', plan),
        ('[SERVICES]', code)
        
    )

    for (i, j) in replace_keys:
        Url = Url.replace(i, j)
        
    api = cableapi.htoken
    # Define the URL and headers
    url = Url
    headers = {
            # Replace with your actual API key
            "Authorization": api,
            "Content-Type": "application/x-www-form-urlencoded"
        }
    response = requests.post(url, headers=headers)
    
    response = response.json()
    
    if any(respo in str(response) for respo in cableapi.success_code.split(",")):
        return {'status': 'SUCCESS', 'response': response}
    else:
        return {'status': 'FAILED', 'response': response}
    


