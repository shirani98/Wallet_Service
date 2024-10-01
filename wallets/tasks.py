from celery import shared_task
from django.utils import timezone
from .models import TaskTracker, Transaction
from django.db import transaction as db_transaction
from .utils import request_third_party_deposit
from django.db.models import F
import uuid


@shared_task
def process_scheduled_withdrawals():
    with db_transaction.atomic():
        pending_withdrawal_ids = list(
            Transaction.objects.select_for_update()
            .filter(
                transaction_type=Transaction.WITHDRAWAL,
                status=Transaction.PENDING,
                timestamp__lte=timezone.now(),
            )
            .values_list("id", flat=True)
        )
        Transaction.objects.filter(id__in=pending_withdrawal_ids).update(
            status=Transaction.INPROGRESS
        )

    for transaction_id in pending_withdrawal_ids:
        process_transaction(transaction_id)


@shared_task(bind=True)
def process_transaction(self, transaction_id):
    task_tracker, created = TaskTracker.objects.get_or_create(
        task_id=uuid.uuid4(), transaction_id=transaction_id
    )
    task_tracker.status = TaskTracker.INPROGRESS
    task_tracker.save(update_fields=["status"])

    transaction = None
    try:
        with db_transaction.atomic():
            transaction = (
                Transaction.objects.select_related("wallet")
                .select_for_update()
                .get(id=transaction_id)
            )
            wallet = transaction.wallet
            task_tracker.transaction = transaction
            if wallet.balance < transaction.amount:
                print("3")
                transaction.status = Transaction.FAILED
                transaction.save(update_fields=["status"])
                task_tracker.status = TaskTracker.SUCCESS
                task_tracker.result = "In2sufficient Balance"
                task_tracker.save(update_fields=["status", "result", "transaction"])
                return

        success = request_third_party_deposit()

        with db_transaction.atomic():
            transaction = (
                Transaction.objects.select_related("wallet")
                .select_for_update()
                .get(id=transaction_id)
            )
            wallet = transaction.wallet

            if success:
                wallet.balance = F("balance") - transaction.amount
                wallet.save(update_fields=["balance"])
                transaction.status = Transaction.SUCCESS
                task_tracker.status = TaskTracker.SUCCESS

            else:
                transaction.status = Transaction.FAILED
                task_tracker.status = TaskTracker.FAILED

            task_tracker.result = {"success": success}
            task_tracker.save(update_fields=["status", "result", "transaction"])
            transaction.save(update_fields=["status"])

    except Exception as e:
        if transaction:
            transaction.status = Transaction.FAILED
            transaction.save(update_fields=["status"])
            task_tracker.status = "FAILED"
        task_tracker.result = {"error": str(e)}
        task_tracker.save(update_fields=["status", "result", "transaction"])
