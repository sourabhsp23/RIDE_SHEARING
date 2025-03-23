from decimal import Decimal
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.api.auth.jwt import get_current_active_user
from app.models.user import User
from app.models.payment import Payment, Wallet, WalletTransaction, PaymentMethod
from app.schemas.payment import (
    Payment as PaymentSchema,
    PaymentCreate,
    Wallet as WalletSchema,
    WalletTransaction as WalletTransactionSchema,
)
from app.services.payment.payment_service import (
    process_payment,
    add_money_to_wallet,
    get_wallet_balance,
    get_wallet_transactions,
)

router = APIRouter()


@router.post("/ride-payment", response_model=PaymentSchema)
async def create_ride_payment(
    *,
    payment_in: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new payment for a ride.
    """
    try:
        payment = await process_payment(
            ride_id=payment_in.ride_id,
            user_id=current_user.id,
            payment_method=payment_in.payment_method,
            amount=payment_in.amount,
        )
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/wallet", response_model=WalletSchema)
async def get_user_wallet(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the current user's wallet.
    """
    wallet = await Wallet.filter(user_id=current_user.id).first()
    if not wallet:
        # Create a new wallet if it doesn't exist
        wallet = await Wallet.create(
            user_id=current_user.id,
            balance=Decimal("0.00"),
        )
    return wallet


@router.post("/wallet/add-money", response_model=WalletSchema)
async def add_to_wallet(
    *,
    amount: Decimal = Body(..., embed=True),
    payment_method: PaymentMethod = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Add money to the current user's wallet.
    """
    try:
        wallet = await add_money_to_wallet(
            user_id=current_user.id,
            amount=amount,
            payment_method=payment_method,
            transaction_details=None,  # In a real app, this would come from the payment gateway
        )
        return wallet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/wallet/transactions", response_model=List[WalletTransactionSchema])
async def get_user_wallet_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the current user's wallet transactions.
    """
    transactions = await get_wallet_transactions(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return transactions


@router.get("/history", response_model=List[PaymentSchema])
async def get_payment_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the current user's payment history.
    """
    payments = await Payment.filter(
        user_id=current_user.id
    ).offset(skip).limit(limit).order_by("-created_at")
    
    return payments 