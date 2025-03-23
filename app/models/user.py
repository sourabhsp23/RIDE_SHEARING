from enum import Enum
from typing import List, Optional

from tortoise import fields
from tortoise.models import Model
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, Enum):
    RIDER = "rider"
    DRIVER = "driver"
    ADMIN = "admin"


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=255, null=True)
    phone_number = fields.CharField(max_length=20, unique=True, index=True)
    role = fields.CharEnumField(UserRole, default=UserRole.RIDER)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Relationships (for example purposes, adjust as needed)
    # rides = fields.ReverseRelation["Ride"]
    # wallet = fields.ReverseRelation["Wallet"]
    
    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    class Meta:
        table = "users" 