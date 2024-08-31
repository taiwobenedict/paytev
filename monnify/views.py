from .models import MonnifyConfig, ProcessedNotification, VirtualAccount
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import hashlib
import hmac
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .services import MonnifyService
from django.contrib import messages
from django.contrib.auth.models import User
from transactions.models import Transactions


@login_required
def generate_virtual_account(request):
    user = request.user
    monnify_service = MonnifyService()

    response_data = monnify_service.generate_virtual_account(user)

    if response_data["requestSuccessful"]:
        response_body = response_data["responseBody"]
        accounts = response_body["accounts"]
        reservation_reference = response_body["reservationReference"]
        status = response_body["status"]

        for account_info in accounts:
            VirtualAccount.objects.create(
                user=user,
                account_number=account_info["accountNumber"],
                bank_name=account_info["bankName"],
                account_name=account_info["accountName"],
                # Use account number as reference
                account_reference=account_info["accountNumber"],
                reservation_reference=reservation_reference,
                status=status
            )
        return redirect('monnify:wallet')
    else:
        messages.error(
            request, response_data["responseMessage"])
        return redirect('monnify:wallet')
        #return render(request, 'account_error.html', {"error": response_data["responseMessage"]})


@login_required
def wallet(request):
    user = request.user
    accounts = VirtualAccount.objects.filter(user=user)
    return render(request, 'bills/monnify.html', {"accounts": accounts})


# views.py
@csrf_exempt
def monnify_webhook(request):
    if request.method == 'POST':
        try:
            request_body = request.body.decode('utf-8')
            received_signature = request.headers.get('monnify-signature')
            config = MonnifyConfig.objects.first()
            secret_key = config.secret_key

            # Compute the hash using the secret key and the request body
            computed_hash = hmac.new(
                secret_key.encode('utf-8'),
                request_body.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()

            # Verify the hash to ensure the request is from Monnify
            if received_signature != computed_hash:
                return JsonResponse({"message": "Invalid signature"}, status=400)

            # Parse the JSON data
            data = json.loads(request_body)
            event_type = data.get('eventType')
            event_data = data.get('eventData')

            if event_type == 'SUCCESSFUL_TRANSACTION':
                transaction_reference = event_data.get('transactionReference')

                # Check if the notification has already been processed
                if ProcessedNotification.objects.filter(transaction_reference=transaction_reference).exists():
                    return JsonResponse({"message": "Notification already processed"}, status=200)

                # Get the account reference and amount paid
                account_number = event_data.get(
                    'destinationAccountInformation', {}).get('accountNumber')
                amount_paid = event_data.get('amountPaid')
                
                m = MonnifyConfig.objects.first()
                fee = m.fee

                # Find the virtual account associated with the account reference
                try:
                    virtual_account = VirtualAccount.objects.get(
                        account_number=account_number)
                    user = virtual_account.user

                    # Credit the user's account
                    # Assuming you have a 'balance' field in the User profile
                    w = user.wallet_credit
                    old = user.wallet_credit
                    a = float(amount_paid) - (float(amount_paid) *
                                      float(fee))
                    #y = w.balance
                    #y = float(y)
                    new = float(user.wallet_credit) + float(a)
                    user.wallet_credit = new
                    user.save()
                    Transactions.objects.create(
                        user=user,
                        bill_type="DEPOSIT",
                        actual_amount=a,
                        old_balance=old,
                        new_balance=user.wallet_credit,
                        
                        status="SUCCESS",
                        reference=transaction_reference,
                        email=user.email,
                    )

                    # Save the processed notification
                    ProcessedNotification.objects.create(
                        transaction_reference=transaction_reference)

                    return JsonResponse({"message": "Webhook received and processed successfully"}, status=200)
                except VirtualAccount.DoesNotExist:
                    return JsonResponse({"message": "Account reference not found"}, status=404)

            else:
                return JsonResponse({"message": "Event type not supported"}, status=400)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)
