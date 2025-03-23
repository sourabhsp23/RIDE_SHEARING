from enum import Enum
from typing import Optional

from tortoise import fields
from tortoise.models import Model


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    WALLET = "wallet"
    UPI = "upi"
    NETBANKING = "netbanking"


class Payment(Model):
    id = fields.IntField(pk=True)
    
    # Relations
    ride = fields.ForeignKeyField('models.Ride', related_name='payments')
    user = fields.ForeignKeyField('models.User', related_name='payments')
    
    # Payment details
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    currency = fields.CharField(max_length=3, default="INR")
    status = fields.CharEnumField(PaymentStatus, default=PaymentStatus.PENDING)
    payment_method = fields.CharEnumField(PaymentMethod)
    
    # Transaction details
    transaction_id = fields.CharField(max_length=255, null=True)
    gateway_response = fields.JSONField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "payments"


class Wallet(Model):
    id = fields.IntField(pk=True)
    
    # Relations
    user = fields.ForeignKeyField('models.User', related_name='wallet')
    
    # Wallet details
    balance = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = fields.CharField(max_length=3, default="INR")
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "wallets"


class WalletTransaction(Model):
    id = fields.IntField(pk=True)
    
    # Relations
    wallet = fields.ForeignKeyField('models.Wallet', related_name='transactions')
    payment = fields.ForeignKeyField('models.Payment', related_name='wallet_transactions', null=True)
    
    # Transaction details
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = fields.CharField(max_length=20)  # credit, debit, refund
    description = fields.CharField(max_length=255)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "wallet_transactions" 