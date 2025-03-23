import asyncio
import random
from typing import List, Optional, Tuple

from app.models.user import User, UserRole
from app.models.ride import Ride, RideStatus


async def find_nearby_drivers(
    latitude: float,
    longitude: float,
    max_distance_km: float = 5.0
) -> List[User]:
    """
    Find drivers near the specified location.
    In a real application, this would use geospatial queries.
    
    For demonstration, we'll just return random available drivers.
    """
    # Get all active drivers
    # In a real app, you would use geospatial queries to find nearby drivers
    drivers = await User.filter(role=UserRole.DRIVER, is_active=True).limit(5)
    
    # Simulate filtering by distance
    # In a real app, this would be done in the database query
    return drivers


async def rank_drivers(
    drivers: List[User],
    ride: Ride
) -> List[Tuple[User, float]]:
    """
    Rank drivers based on various factors like distance, rating, etc.
    
    In a real application, this would use an ML model for intelligent ranking.
    """
    ranked_drivers = []
    
    for driver in drivers:
        # In a real app, these would be actual metrics
        # For demonstration, we'll use random scores
        distance_score = random.uniform(0, 1)  # Lower is better
        rating_score = random.uniform(0, 1)    # Higher is better
        acceptance_rate = random.uniform(0, 1) # Higher is better
        
        # Combined score (in a real app, this would use a more sophisticated algorithm)
        score = (1 - distance_score) * 0.5 + rating_score * 0.3 + acceptance_rate * 0.2
        
        ranked_drivers.append((driver, score))
    
    # Sort by score, highest first
    ranked_drivers.sort(key=lambda x: x[1], reverse=True)
    
    return ranked_drivers


async def match_ride_with_driver(ride_id: int) -> Optional[User]:
    """
    Match a ride with the best available driver.
    This is a background task that is run when a ride is created.
    """
    # Get the ride
    ride = await Ride.filter(id=ride_id).first()
    if not ride or ride.status != RideStatus.REQUESTED:
        return None
    
    # Find nearby drivers
    nearby_drivers = await find_nearby_drivers(
        latitude=ride.pickup_latitude,
        longitude=ride.pickup_longitude
    )
    
    if not nearby_drivers:
        # No drivers available
        return None
    
    # Rank drivers
    ranked_drivers = await rank_drivers(nearby_drivers, ride)
    
    # In a real application, you would:
    # 1. Send a notification to the top-ranked driver
    # 2. Wait for their response
    # 3. If they decline or timeout, try the next driver
    
    # For demonstration, we'll simply select the top-ranked driver
    if ranked_drivers:
        best_driver, _ = ranked_drivers[0]
        
        # Assign the driver to the ride
        ride.driver = best_driver
        ride.status = RideStatus.ACCEPTED
        await ride.save()
        
        # In a real app, send notifications to both rider and driver
        
        return best_driver
    
    return None


async def simulate_driver_matching(ride_id: int) -> None:
    """
    Simulate the process of matching a ride with a driver.
    In a real application, this would happen through push notifications.
    """
    # Wait a few seconds to simulate processing time
    await asyncio.sleep(5)
    
    # Match the ride with a driver
    matched_driver = await match_ride_with_driver(ride_id)
    
    # If no driver was found, update the ride status
    if not matched_driver:
        ride = await Ride.filter(id=ride_id).first()
        if ride and ride.status == RideStatus.REQUESTED:
            # No driver found after timeout
            # In a real app, you might retry or notify the user
            pass 