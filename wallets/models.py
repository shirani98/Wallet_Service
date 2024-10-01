import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Wallet(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.CharField(max_length=100)

    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"Wallet owned by {self.user} with balance {self.balance}"

    def deposit(self, amount: int):
        # todo: deposit the amount into this wallet
        pass


class Transaction(models.Model):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

    FAILED = "failed"
    SUCCESS = "success"
    PENDING = "pending"
    INPROGRESS = "inprogress"

    TRANSACTION_TYPE_CHOICES = [(DEPOSIT, "Deposit"), (WITHDRAWAL, "Withdrawal")]

    TRANSACTION_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10, choices=TRANSACTION_STATUS_CHOICES, default=PENDING
    )

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} for {self.wallet.user}"


class TaskTracker(models.Model):
    FAILED = "failed"
    SUCCESS = "success"
    PENDING = "pending"
    INPROGRESS = "inprogress"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (INPROGRESS, "Processing"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]

    task_id = models.CharField(max_length=255, unique=True)
    transaction = models.ForeignKey(
        "Transaction", on_delete=models.CASCADE, related_name="task_tracker"
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task {self.task_id} - {self.status}"
