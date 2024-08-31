from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import StrowalletAccount, Hooklog
from account.models import CustomUser
from .utils import create_strowallet_account, verify_transaction
import logging
import os
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Hooklog



@login_required
def create_virtual_account(request):
    account_info = None  # Initialize account_info

    if request.method == 'POST':
        user = request.user
        account_info = create_strowallet_account(user)
        
        if account_info and account_info.get('success'):
            # Create the StrowalletAccount in the database
            StrowalletAccount.objects.create(
                user=user,
                account_number=account_info.get('account_number'),
                account_name=account_info.get('account_name'),
                bank_name=account_info.get('bank_name'),
                bank_code=account_info.get('bank_code', ''),  # Handle missing bank_code
                customer_email=user.email
            )
            print(f"Account created successfully: {account_info}")  # Debugging line
            return redirect('view_virtual_account')
        else:
            # Pass the detailed message from the API response
            error_message = account_info.get('message', 'Failed to create account.')
            print(f"Failed to create account. Response: {account_info}")  # Debugging line
            return render(request, 'strowallet/create_account.html', {'account_info': account_info, 'error_message': error_message})

    return render(request, 'strowallet/create_account.html', {'account_info': account_info})





@login_required
def view_virtual_account(request):
    try:
        account = StrowalletAccount.objects.get(user=request.user)
        return render(request, 'strowallet/view_account.html', {'account': account})
    except StrowalletAccount.DoesNotExist:
        # Handle the case where the account does not exist
        return render(request, 'strowallet/no_account.html')





@csrf_exempt
def webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get('sessionId')
            if not session_id:
                return JsonResponse({"error": "Missing sessionId"}, status=400)

            # Verify the transaction
            response_data = verify_transaction(session_id)
            
            # Log webhook data
            Hooklog.objects.create(myhook=json.dumps(data))

            # Check the response and process accordingly
            if response_data.get('status') == 'success':
                # Add settled amount to user's wallet
                account_number = data.get('accountNumber')
                settled_amount = data.get('settledAmount')
                try:
                    strowallet_account = StrowalletAccount.objects.get(account_number=account_number)
                    user = strowallet_account.user
                    user.wallet_credit += settled_amount
                    user.save()
                    return JsonResponse({"status": "success"}, status=200)
                except StrowalletAccount.DoesNotExist:
                    return JsonResponse({"error": "Account not found"}, status=404)
            else:
                return JsonResponse({"error": "Transaction not successful"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
