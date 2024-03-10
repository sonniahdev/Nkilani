import requests
from decouple import config

PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY")


def initialize_transaction(email, amount, card_number, expiration_month, expiration_year, cvc):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": amount,
        "currency": "KES",
        "card": {
            "number": card_number,
            "cvv": cvc,
            "expiry_month": expiration_month,
            "expiry_year": expiration_year
        }
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    # send to M-PESA Paybil (on testing)....
    # withdrawal_requests(amount)

    return response_data


def verify_transaction(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"{PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    return response.json()


def create_transfer_recipient_mobile_money(mobile_number, telco_code, currency, name):
    url = "https://api.paystack.co/transferrecipient"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "mobile_money",
        "name": name,
        "account_number": mobile_number,
        "bank_code": telco_code,
        "currency": currency
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


def send_money_to_mobile(recipient_code, amount, reference):
    url = "https://api.paystack.co/transfer"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "source": "balance",
        "reason": "Payment to Mobile Money",
        "amount": amount,
        "recipient": recipient_code,
        "reference": reference
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


def withdrawal_requests(amount):
    recipient_response = create_transfer_recipient_mobile_money("0712345678", "SAF", "KES", "Bradley Okeno")

    if 'data' in recipient_response:
        recipient_code = recipient_response['data']['recipient_code']
        transfer_response = send_money_to_mobile(recipient_code, amount, "payment123")
        print(transfer_response)
    else:
        print("Error: 'data' key not found in recipient_response")