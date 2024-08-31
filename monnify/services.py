import random
import string
import requests
from .models import MonnifyConfig
import requests
import json
from base64 import b64encode
from django.contrib.auth.models import User



class MonnifyService:
    def __init__(self):
        config = MonnifyConfig.objects.first()
        self.base_url = config.base_url
        self.api_key = config.api_key
        self.secret_key = config.secret_key
        self.contract_code = config.contract_code

    def generate_account_reference(self):
        #Generate a random 10-character string for account reference.
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    def get_auth_token(self):
        url = f"{self.base_url}/api/v1/auth/login"
        credentials = f"{self.api_key}:{self.secret_key}".encode('ascii')
        encoded_credentials = b64encode(credentials).decode('ascii')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}"
        }
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            if "responseBody" in response_data and "accessToken" in response_data["responseBody"]:
                return response_data["responseBody"]["accessToken"]
            else:
                raise KeyError(
                    "Expected keys are not present in the response.")
        else:
            response_data = response.json()
            error_message = response_data.get(
                "error_description", "Unknown error")
            raise Exception(f"Error getting token: {error_message}")

    def generate_virtual_account(self, user):
        url = f"{self.base_url}/api/v2/bank-transfer/reserved-accounts"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_auth_token()}",
        }
        payload = {
            "accountReference": self.generate_account_reference(),
            "accountName": user.username,
            "customerEmail": user.email,
            "customerName": user.username,
            "contractCode": self.contract_code,
            "currencyCode": "NGN",
            "getAllAvailableBanks": True
        }
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        return response_data
