import requests
from .models import Transaction
from django.db import transaction as db_transaction
from django.db.models import F


def request_third_party_deposit():
    response = requests.post("http://localhost:8010/")
    return response.json()
