from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Ride-Sharing API Test")

class RideRequest(BaseModel):
    pickup_location: str
    destination: str
    user_id: int

@app.get("/")
async def root():
    return {"message": "Welcome to the Ride-Sharing API"}

@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "version": "1.0.0",
        "services": ["user", "ride", "payment"]
    }

@app.post("/api/rides/request")
async def request_ride(ride: RideRequest):
    # In a real app, this would interact with databases and models
    return {
        "ride_id": 12345,
        "status": "requested",
        "estimated_fare": 150.0,
        "estimated_time": "10 minutes",
        "driver": {
            "id": 789,
            "name": "John Driver",
            "rating": 4.8
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_app:app", host="0.0.0.0", port=8000, reload=True) 