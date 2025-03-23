from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth.jwt import get_current_active_user
from app.models.user import User, UserRole
from app.models.ride import Ride, RideStatus
from app.schemas.user import User as UserSchema
from app.schemas.ride import Ride as RideSchema

router = APIRouter()


@router.get("/available", response_model=List[UserSchema])
async def get_available_drivers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all available drivers.
    Only admin users can access this endpoint.
    """
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get active drivers
    drivers = await User.filter(
        role=UserRole.DRIVER,
        is_active=True,
    ).offset(skip).limit(limit)
    
    return drivers


@router.get("/me/rides", response_model=List[RideSchema])
async def get_driver_rides(
    status: RideStatus = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all rides for the current driver.
    """
    # Check if user is a driver
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a driver",
        )
    
    # Build filters
    filters = {"driver_id": current_user.id}
    if status:
        filters["status"] = status
    
    # Get rides
    rides = await Ride.filter(**filters).offset(skip).limit(limit).order_by("-created_at")
    
    return rides


@router.put("/me/status/{is_active}", response_model=UserSchema)
async def update_driver_status(
    is_active: bool,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update driver availability status.
    """
    # Check if user is a driver
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a driver",
        )
    
    # Check if driver has ongoing rides
    if is_active is False:
        active_rides = await Ride.filter(
            driver_id=current_user.id,
            status__in=[RideStatus.ACCEPTED, RideStatus.ARRIVED, RideStatus.IN_PROGRESS],
        ).count()
        
        if active_rides > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set status to inactive with ongoing rides",
            )
    
    # Update driver status
    current_user.is_active = is_active
    await current_user.save()
    
    return current_user


@router.post("/me/location", status_code=status.HTTP_204_NO_CONTENT)
async def update_driver_location(
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Update driver's current location.
    In a real app, this would be stored in a real-time database or cache.
    """
    # Check if user is a driver
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a driver",
        )
    
    # In a real application, you would store the driver's location
    # in a real-time database or cache like Redis
    # For demonstration purposes, we'll just return a success status
    
    # Example code for a real implementation:
    # await redis.hset(
    #     f"driver:location:{current_user.id}",
    #     mapping={
    #         "latitude": latitude,
    #         "longitude": longitude,
    #         "updated_at": datetime.utcnow().timestamp()
    #     }
    # )
    
    return None


@router.get("/me/rides/current", response_model=RideSchema)
async def get_current_ride(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the driver's current active ride.
    """
    # Check if user is a driver
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a driver",
        )
    
    # Get active ride
    active_ride = await Ride.filter(
        driver_id=current_user.id,
        status__in=[
            RideStatus.ACCEPTED,
            RideStatus.ARRIVED,
            RideStatus.IN_PROGRESS
        ]
    ).first()
    
    if not active_ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active ride found",
        )
    
    return active_ride 