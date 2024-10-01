from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from django.db import transaction as db_transaction
from .models import Wallet, Transaction
from wallets.serializers import WalletSerializer
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import F


class CreateWalletView(CreateAPIView):
    serializer_class = WalletSerializer


class RetrieveWalletView(RetrieveAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
    lookup_field = "uuid"


class CreateDepositView(APIView):
    def post(self, request, uuid):
        amount = request.data.get("amount")

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(uuid=uuid)
            wallet.balance = F("balance") + Decimal(amount)
            wallet.save()

            Transaction.objects.create(
                wallet=wallet,
                transaction_type=Transaction.DEPOSIT,
                status=Transaction.SUCCESS,
                amount=amount,
            )

        return JsonResponse({"status": "success", "balance": str(wallet.balance)})


class ScheduleWithdrawView(APIView):
    def post(self, request, uuid):

        amount = request.data.get("amount")
        timestamp = request.data.get("timestamp")

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(uuid=uuid)
            Transaction.objects.create(
                wallet=wallet,
                transaction_type=Transaction.WITHDRAWAL,
                amount=amount,
                status=Transaction.PENDING,
                timestamp=timestamp,
            )

        return JsonResponse({"status": "scheduled", "balance": wallet.balance})
