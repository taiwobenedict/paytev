import requests
from django.conf import settings
from .models import StrowalletConfig, Hooklog

def get_strowallet_config():
    return StrowalletConfig.objects.first()

def create_strowallet_account(user):
    config = get_strowallet_config()
    url = "https://strowallet.com/api/virtual-bank/new-customer"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "public_key": config.public_key,
        "email": user.email,
        "account_name": user.get_full_name(),
        "phone": user.phone_number,  
        "webhook_url": "https://severely-model-ghost.ngrok-free.app/strowallet/webhook/"
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Response Status Code: {response.status_code}")  # Debugging line
    print(f"Response Content: {response.content}")  # Debugging line
    if response.status_code == 200:
        return response.json()
    return {"success": False, "message": "Failed to create account."}



import logging
import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from .models import StrowalletConfig, Hooklog
from .models import Hooklog, StrowalletAccount
from account.models import CustomUser
import requests
import logging 

logger = logging.getLogger('strowallet')

def verify_transaction(session_id, amount):
    strowallet_config = StrowalletConfig.objects.first()
    secret_key = strowallet_config.secret_key

    url = f"https://api.strowallet.com/v1/transactions/{session_id}/verify"
    headers = {
        "Authorization": f"Bearer {secret_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        logger.debug(f"Verify Transaction Status Code: {response.status_code}")
        logger.debug(f"Verify Transaction Response: {response.json()}")

        if response.status_code == 200:
            response_data = response.json()
            Hooklog.objects.create(myhook=response_data)

            # Adjust this condition based on the actual response structure
            if response_data.get("status") == 200 and response_data.get("message") == 'Transaction received.':
                # Fetch the StrowalletAccount using the account number from the webhook data
                account = StrowalletAccount.objects.get(account_number=response_data.get('accountNumber'))

                # Update the user's wallet balance
                user = account.user
                user.wallet_credit += response_data.get('settledAmount', 0)
                user.save()

                return True

        return False

    except Exception as e:
        logger.error(f"Error in verify_transaction: {e}")
        return False
