from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.api.auth.jwt import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema

router = APIRouter()


@router.post("/", response_model=UserSchema)
async def create_user(*, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    # Check if user with this email exists
    user = await User.filter(email=user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )
    
    # Check if user with this phone exists
    user = await User.filter(phone_number=user_in.phone_number).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this phone number already exists.",
        )
    
    # Create new user
    user_data = user_in.dict(exclude={"password"})
    user_obj = User(**user_data)
    user_obj.hashed_password = User.get_password_hash(user_in.password)
    await user_obj.save()
    return user_obj


@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_me(
    *,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user.
    """
    user_data = jsonable_encoder(current_user)
    update_data = user_in.dict(exclude_unset=True)
    
    # Handle password update separately
    if "password" in update_data and update_data["password"]:
        hashed_password = User.get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    # Update user
    for field in user_data:
        if field in update_data:
            setattr(current_user, field, update_data[field])
    
    await current_user.save()
    return current_user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    """
    # Only admin users can access other users' data
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user 