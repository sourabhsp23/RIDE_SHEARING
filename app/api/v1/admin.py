from typing import Any, Dict, List
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth.jwt import get_current_active_user
from app.models.user import User, UserRole
from app.models.ride import Ride, RideStatus

router = APIRouter()


# Helper function to verify admin access
async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Verify the current user is an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


@router.get("/users", response_model=List[Dict[str, Any]])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(get_current_admin_user),
) -> Any:
    """
    Get all users (admin only).
    """
    users = await User.all().offset(skip).limit(limit)
    
    # Convert to dict for response
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_stats(
    _: User = Depends(get_current_admin_user),
) -> Any:
    """
    Get dashboard statistics (admin only).
    """
    # Get counts
    total_users = await User.all().count()
    total_riders = await User.filter(role=UserRole.RIDER).count()
    total_drivers = await User.filter(role=UserRole.DRIVER).count()
    
    total_rides = await Ride.all().count()
    completed_rides = await Ride.filter(status=RideStatus.COMPLETED).count()
    cancelled_rides = await Ride.filter(status=RideStatus.CANCELLED).count()
    
    # In a real application, these would be calculated from actual data
    # For demonstration, we'll use random values
    
    # Average metrics
    avg_ride_distance = round(random.uniform(5, 15), 2)  # km
    avg_ride_duration = round(random.uniform(15, 45))  # minutes
    avg_ride_fare = round(random.uniform(100, 300), 2)  # currency
    
    # Calculate ride statistics by hour of day
    # In a real app, this would be an aggregation query
    ride_by_hour = [
        {"hour": hour, "count": random.randint(10, 100)}
        for hour in range(24)
    ]
    
    # Top 5 busiest areas
    top_areas = [
        {"name": "Downtown", "rides": random.randint(50, 200)},
        {"name": "Airport", "rides": random.randint(40, 180)},
        {"name": "University", "rides": random.randint(30, 150)},
        {"name": "Shopping Mall", "rides": random.randint(20, 120)},
        {"name": "Business District", "rides": random.randint(10, 100)},
    ]
    
    return {
        "user_stats": {
            "total_users": total_users,
            "total_riders": total_riders,
            "total_drivers": total_drivers,
        },
        "ride_stats": {
            "total_rides": total_rides,
            "completed_rides": completed_rides,
            "cancelled_rides": cancelled_rides,
            "avg_ride_distance": avg_ride_distance,
            "avg_ride_duration": avg_ride_duration,
            "avg_ride_fare": avg_ride_fare,
        },
        "charts": {
            "ride_by_hour": ride_by_hour,
            "top_areas": top_areas,
        }
    }


@router.get("/forecast", response_model=Dict[str, Any])
async def get_demand_forecast(
    _: User = Depends(get_current_admin_user),
) -> Any:
    """
    Get demand forecast for the next 24 hours (admin only).
    In a real application, this would use ML models.
    """
    # Current time
    now = datetime.utcnow()
    
    # Generate forecast for the next 24 hours
    hourly_forecast = []
    
    for hour in range(24):
        forecast_time = now + timedelta(hours=hour)
        
        # In a real app, this would use ML predictions
        # For demonstration, we'll use a simple pattern with some randomness
        
        # Basic pattern: higher during morning and evening rush hours
        hour_of_day = forecast_time.hour
        
        # Base demand based on time of day
        if 7 <= hour_of_day <= 9:  # Morning rush
            base_demand = random.uniform(0.7, 0.9)
        elif 16 <= hour_of_day <= 19:  # Evening rush
            base_demand = random.uniform(0.8, 1.0)
        elif 22 <= hour_of_day or hour_of_day <= 5:  # Night
            base_demand = random.uniform(0.3, 0.5)
        else:  # Regular hours
            base_demand = random.uniform(0.4, 0.6)
        
        # Add some randomness
        demand = base_demand + random.uniform(-0.1, 0.1)
        demand = max(0, min(1, demand))  # Clamp between 0 and 1
        
        # Surge pricing recommendation
        if demand > 0.8:
            surge_recommendation = random.uniform(1.8, 2.0)
        elif demand > 0.6:
            surge_recommendation = random.uniform(1.4, 1.7)
        elif demand > 0.4:
            surge_recommendation = random.uniform(1.1, 1.3)
        else:
            surge_recommendation = 1.0
        
        hourly_forecast.append({
            "hour": forecast_time.strftime("%H:00"),
            "demand": round(demand, 2),
            "surge_recommendation": round(surge_recommendation, 1),
        })
    
    # Area-based forecast
    area_forecast = [
        {
            "area": "Downtown",
            "demand": round(random.uniform(0.5, 0.9), 2),
            "forecast_drivers_needed": random.randint(10, 30),
        },
        {
            "area": "Airport",
            "demand": round(random.uniform(0.4, 0.8), 2),
            "forecast_drivers_needed": random.randint(5, 20),
        },
        {
            "area": "University",
            "demand": round(random.uniform(0.3, 0.7), 2),
            "forecast_drivers_needed": random.randint(5, 15),
        },
        {
            "area": "Shopping Mall",
            "demand": round(random.uniform(0.4, 0.6), 2),
            "forecast_drivers_needed": random.randint(7, 18),
        },
        {
            "area": "Business District",
            "demand": round(random.uniform(0.5, 0.8), 2),
            "forecast_drivers_needed": random.randint(8, 25),
        },
    ]
    
    return {
        "hourly_forecast": hourly_forecast,
        "area_forecast": area_forecast,
    } 