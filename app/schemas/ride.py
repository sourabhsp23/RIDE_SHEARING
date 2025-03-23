from typing import Optional
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.ride import RideStatus


# Shared properties
class RideLocationBase(BaseModel):
    latitude: float
    longitude: float
    address: str


class RideBase(BaseModel):
    pickup_latitude: float
    pickup_longitude: float
    pickup_address: str
    destination_latitude: float
    destination_longitude: float
    destination_address: str


# Properties to receive via API on creation
class RideCreate(RideBase):
    pass


# Properties to receive via API on update
class RideUpdate(BaseModel):
    status: Optional[RideStatus] = None


# Properties shared by models stored in DB
class RideInDBBase(RideBase):
    id: int
    rider_id: int
    driver_id: Optional[int] = None
    status: RideStatus
    fare: Optional[Decimal] = None
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    estimated_fare: Optional[Decimal] = None
    estimated_duration_minutes: Optional[int] = None
    estimated_distance_km: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    route_deviation_detected: bool
    sos_triggered: bool

    class Config:
        orm_mode = True


# Additional properties to return via API
class Ride(RideInDBBase):
    pass


# Additional properties to receive in ride request
class RideRequest(RideBase):
    pass


# Response for ride estimate
class RideEstimate(BaseModel):
    estimated_fare: Decimal
    estimated_duration_minutes: int
    estimated_distance_km: float


# Response for tracking ride
class RideTracking(BaseModel):
    ride_id: int
    current_latitude: float
    current_longitude: float
    estimated_arrival_minutes: int
    status: RideStatus 