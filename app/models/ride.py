from enum import Enum
from typing import Optional

from tortoise import fields
from tortoise.models import Model


class RideStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    ARRIVED = "arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Ride(Model):
    id = fields.IntField(pk=True)
    
    # Relations
    rider = fields.ForeignKeyField('models.User', related_name='rides_as_rider')
    driver = fields.ForeignKeyField('models.User', related_name='rides_as_driver', null=True)
    
    # Location details
    pickup_latitude = fields.FloatField()
    pickup_longitude = fields.FloatField()
    pickup_address = fields.CharField(max_length=255)
    
    destination_latitude = fields.FloatField()
    destination_longitude = fields.FloatField()
    destination_address = fields.CharField(max_length=255)
    
    # Ride details
    status = fields.CharEnumField(RideStatus, default=RideStatus.REQUESTED)
    fare = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    distance_km = fields.FloatField(null=True)
    duration_minutes = fields.IntField(null=True)
    
    # AI-generated fields
    estimated_fare = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    estimated_duration_minutes = fields.IntField(null=True)
    estimated_distance_km = fields.FloatField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    
    # Safety features
    route_deviation_detected = fields.BooleanField(default=False)
    sos_triggered = fields.BooleanField(default=False)
    
    class Meta:
        table = "rides" 