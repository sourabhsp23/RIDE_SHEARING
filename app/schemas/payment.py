from typing import Any, Dict, Optional
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.payment import PaymentStatus, PaymentMethod


# Payment Schemas
class PaymentBase(BaseModel):
    amount: Decimal
    currency: str = "INR"
    payment_method: PaymentMethod


class PaymentCreate(PaymentBase):
    ride_id: int


class PaymentInDBBase(PaymentBase):
    id: int
    ride_id: int
    user_id: int
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Payment(PaymentInDBBase):
    pass


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None


# Wallet Schemas
class WalletBase(BaseModel):
    balance: Decimal
    currency: str = "INR"


class WalletCreate(BaseModel):
    user_id: int


class WalletInDBBase(WalletBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Wallet(WalletInDBBase):
    pass


# Wallet Transaction Schemas
class WalletTransactionBase(BaseModel):
    amount: Decimal
    transaction_type: str
    description: str


class WalletTransactionCreate(WalletTransactionBase):
    wallet_id: int
    payment_id: Optional[int] = None


class WalletTransactionInDBBase(WalletTransactionBase):
    id: int
    wallet_id: int
    payment_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True


class WalletTransaction(WalletTransactionInDBBase):
    pass 