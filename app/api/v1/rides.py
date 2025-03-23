from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from app.api.auth.jwt import get_current_active_user
from app.models.user import User, UserRole
from app.models.ride import Ride, RideStatus
from app.schemas.ride import RideCreate, RideUpdate, Ride as RideSchema, RideEstimate, RideRequest, RideTracking
from app.services.ride_matching.matching import match_ride_with_driver
from app.services.ride_matching.fare_estimator import estimate_fare

router = APIRouter()


@router.post("/request", response_model=RideEstimate)
async def request_ride_estimate(
    *,
    ride_in: RideRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Request a ride estimate without creating a ride.
    """
    # Ensure the user is a rider
    if current_user.role != UserRole.RIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only riders can request rides",
        )
    
    # Calculate estimate using AI model
    estimate = await estimate_fare(
        pickup_latitude=ride_in.pickup_latitude,
        pickup_longitude=ride_in.pickup_longitude,
        destination_latitude=ride_in.destination_latitude,
        destination_longitude=ride_in.destination_longitude,
    )
    
    return estimate


@router.post("/", response_model=RideSchema)
async def create_ride(
    *,
    ride_in: RideCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new ride.
    """
    # Ensure the user is a rider
    if current_user.role != UserRole.RIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only riders can create rides",
        )
    
    # Check if user has an active ride
    active_ride = await Ride.filter(
        rider_id=current_user.id,
        status__in=[
            RideStatus.REQUESTED,
            RideStatus.ACCEPTED,
            RideStatus.ARRIVED,
            RideStatus.IN_PROGRESS
        ]
    ).first()
    
    if active_ride:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active ride",
        )
    
    # Calculate estimate using AI model
    estimate = await estimate_fare(
        pickup_latitude=ride_in.pickup_latitude,
        pickup_longitude=ride_in.pickup_longitude,
        destination_latitude=ride_in.destination_latitude,
        destination_longitude=ride_in.destination_longitude,
    )
    
    # Create ride object
    ride_data = ride_in.dict()
    ride_obj = Ride(**ride_data)
    ride_obj.rider = current_user
    ride_obj.estimated_fare = estimate.estimated_fare
    ride_obj.estimated_duration_minutes = estimate.estimated_duration_minutes
    ride_obj.estimated_distance_km = estimate.estimated_distance_km
    await ride_obj.save()
    
    # Start the driver matching process in the background
    background_tasks.add_task(
        match_ride_with_driver,
        ride_id=ride_obj.id
    )
    
    return ride_obj


@router.get("/", response_model=List[RideSchema])
async def read_rides(
    *,
    skip: int = 0,
    limit: int = 100,
    status: Optional[RideStatus] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve rides.
    """
    # Build filter conditions
    filters = {}
    
    # Only admins can see all rides
    if current_user.role != UserRole.ADMIN:
        if current_user.role == UserRole.RIDER:
            filters["rider_id"] = current_user.id
        else:  # Driver
            filters["driver_id"] = current_user.id
    
    # Filter by status if provided
    if status:
        filters["status"] = status
    
    # Fetch rides
    rides = await Ride.filter(**filters).offset(skip).limit(limit).order_by("-created_at")
    return rides


@router.get("/{ride_id}", response_model=RideSchema)
async def read_ride(
    *,
    ride_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get specific ride by ID.
    """
    ride = await Ride.filter(id=ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found",
        )
    
    # Check if user has permissions to see this ride
    if (current_user.role != UserRole.ADMIN and 
        current_user.id != ride.rider_id and 
        current_user.id != ride.driver_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this ride",
        )
    
    return ride


@router.put("/{ride_id}", response_model=RideSchema)
async def update_ride_status(
    *,
    ride_id: int,
    ride_in: RideUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update ride status.
    """
    ride = await Ride.filter(id=ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found",
        )
    
    # Check if user has permissions to update this ride
    if (current_user.role != UserRole.ADMIN and 
        current_user.id != ride.rider_id and 
        current_user.id != ride.driver_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this ride",
        )
    
    # Validate status transitions
    if ride_in.status and ride_in.status != ride.status:
        # Here you would implement logic to validate status transitions
        # For example: a ride can only go from REQUESTED to ACCEPTED or CANCELLED
        # For simplicity, we'll accept any transition for now
        ride.status = ride_in.status
        
        # Update timestamps based on status
        if ride_in.status == RideStatus.IN_PROGRESS and not ride.started_at:
            ride.started_at = datetime.utcnow()
        elif ride_in.status == RideStatus.COMPLETED and not ride.completed_at:
            ride.completed_at = datetime.utcnow()
    
    await ride.save()
    return ride


@router.post("/{ride_id}/sos", response_model=RideSchema)
async def trigger_sos(
    *,
    ride_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Trigger SOS for a ride.
    """
    ride = await Ride.filter(id=ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found",
        )
    
    # Check if user is part of this ride
    if current_user.id != ride.rider_id and current_user.id != ride.driver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to trigger SOS for this ride",
        )
    
    # Update SOS status
    ride.sos_triggered = True
    await ride.save()
    
    # In a real application, you would also:
    # 1. Send notifications to emergency contacts
    # 2. Alert administrators
    # 3. Potentially contact emergency services
    
    return ride


@router.post("/{ride_id}/cancel", response_model=RideSchema)
async def cancel_ride(
    *,
    ride_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Cancel a ride.
    """
    ride = await Ride.filter(id=ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found",
        )
    
    # Check if user is the rider or an admin
    if current_user.id != ride.rider_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the rider or admin can cancel a ride",
        )
    
    # Check if ride can be cancelled (not already completed or cancelled)
    if ride.status in [RideStatus.COMPLETED, RideStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a ride that is already {ride.status}",
        )
    
    # Update ride status
    ride.status = RideStatus.CANCELLED
    await ride.save()
    
    return ride


@router.websocket("/track/{ride_id}")
async def track_ride(websocket: WebSocket, ride_id: int):
    """
    WebSocket endpoint for real-time ride tracking.
    """
    await websocket.accept()
    try:
        # In a real application, you would:
        # 1. Authenticate the WebSocket connection
        # 2. Verify the user has access to this ride
        # 3. Subscribe to location updates from the driver
        # 4. Send real-time updates to the client
        
        # For demonstration, we'll simulate location updates
        ride = await Ride.filter(id=ride_id).first()
        if not ride:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Example of sending tracking data
        tracking_data = RideTracking(
            ride_id=ride.id,
            current_latitude=ride.pickup_latitude,  # In a real app, this would be the driver's current location
            current_longitude=ride.pickup_longitude,
            estimated_arrival_minutes=5,  # This would be calculated in real-time
            status=ride.status
        )
        
        await websocket.send_json(jsonable_encoder(tracking_data))
        
        # Keep the connection open for a while
        # In a real app, you'd continue sending updates
        while True:
            # Wait for messages (could be used for client interaction)
            data = await websocket.receive_text()
            # Process client messages if needed
            
    except WebSocketDisconnect:
        # Handle disconnection
        pass 