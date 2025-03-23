from fastapi import FastAPI

app = FastAPI(title="Ride-Sharing API")

@app.get("/")
def home():
    return {"message": "Welcome to the Ride-Sharing API"}

@app.get("/api/rides")
def get_rides():
    return [
        {
            "id": 1,
            "from": "Downtown",
            "to": "Airport",
            "status": "completed",
            "fare": 250
        },
        {
            "id": 2,
            "from": "Mall",
            "to": "Beach",
            "status": "in_progress",
            "fare": 180
        }
    ]

@app.get("/api/drivers")
def get_drivers():
    return [
        {"id": 101, "name": "John Driver", "rating": 4.8},
        {"id": 102, "name": "Alice Driver", "rating": 4.9}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("minimal_app:app", host="127.0.0.1", port=8000) 