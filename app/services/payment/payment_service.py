from decimal import Decimal
from typing import Dict, Optional, Any

from app.models.payment import Payment, Wallet, WalletTransaction, PaymentStatus, PaymentMethod
from app.models.user import User
from app.models.ride import Ride, RideStatus
from app.core.config import settings


async def process_payment(
    ride_id: int,
    user_id: int,
    payment_method: PaymentMethod,
    amount: Decimal
) -> Payment:
    """
    Process a payment for a ride.
    """
    # Get the ride
    ride = await Ride.filter(id=ride_id).first()
    if not ride:
        raise ValueError("Ride not found")
    
    # Verify ride belongs to the user
    if ride.rider_id != user_id:
        raise ValueError("Ride does not belong to the user")
    
    # Verify ride is completed
    if ride.status != RideStatus.COMPLETED:
        raise ValueError(f"Cannot process payment for ride with status {ride.status}")
    
    # Create payment
    payment = await Payment.create(
        ride=ride,
        user_id=user_id,
        amount=amount,
        payment_method=payment_method,
        status=PaymentStatus.PENDING
    )
    
    # Process payment based on method
    if payment_method == PaymentMethod.WALLET:
        await process_wallet_payment(payment)
    else:
        # For other payment methods, we would integrate with a payment gateway
        # For demonstration, we'll just mark it as completed
        payment.status = PaymentStatus.COMPLETED
        await payment.save()
    
    return payment


async def process_wallet_payment(payment: Payment) -> None:
    """
    Process a payment using the user's wallet.
    """
    # Get user's wallet
    wallet = await Wallet.filter(user_id=payment.user_id).first()
    if not wallet:
        # Create wallet if it doesn't exist
        wallet = await Wallet.create(
            user_id=payment.user_id,
            balance=Decimal("0.00")
        )
    
    # Check if wallet has sufficient balance
    if wallet.balance < payment.amount:
        payment.status = PaymentStatus.FAILED
        await payment.save()
        raise ValueError("Insufficient wallet balance")
    
    # Deduct from wallet
    wallet.balance -= payment.amount
    await wallet.save()
    
    # Create wallet transaction
    await WalletTransaction.create(
        wallet=wallet,
        payment=payment,
        amount=payment.amount,
        transaction_type="debit",
        description=f"Payment for ride #{payment.ride_id}"
    )
    
    # Update payment status
    payment.status = PaymentStatus.COMPLETED
    await payment.save()


async def add_money_to_wallet(
    user_id: int,
    amount: Decimal,
    payment_method: PaymentMethod,
    transaction_details: Optional[Dict[str, Any]] = None
) -> Wallet:
    """
    Add money to a user's wallet.
    """
    # Get user's wallet
    wallet = await Wallet.filter(user_id=user_id).first()
    if not wallet:
        # Create wallet if it doesn't exist
        wallet = await Wallet.create(
            user_id=user_id,
            balance=Decimal("0.00")
        )
    
    # In a real application, you would process the payment through a payment gateway
    # For demonstration, we'll just add the money directly
    
    # Create a payment record
    payment = await Payment.create(
        user_id=user_id,
        amount=amount,
        payment_method=payment_method,
        status=PaymentStatus.COMPLETED,
        transaction_id=transaction_details.get("transaction_id") if transaction_details else None,
        gateway_response=transaction_details
    )
    
    # Add money to wallet
    wallet.balance += amount
    await wallet.save()
    
    # Create wallet transaction
    await WalletTransaction.create(
        wallet=wallet,
        payment=payment,
        amount=amount,
        transaction_type="credit",
        description="Added money to wallet"
    )
    
    return wallet


async def get_wallet_balance(user_id: int) -> Decimal:
    """
    Get a user's wallet balance.
    """
    wallet = await Wallet.filter(user_id=user_id).first()
    if not wallet:
        return Decimal("0.00")
    
    return wallet.balance


async def get_wallet_transactions(
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> list:
    """
    Get a user's wallet transactions.
    """
    wallet = await Wallet.filter(user_id=user_id).first()
    if not wallet:
        return []
    
    transactions = await WalletTransaction.filter(
        wallet_id=wallet.id
    ).offset(skip).limit(limit).order_by("-created_at")
    
    return transactions 