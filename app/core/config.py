import secrets
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # Server settings
    PROJECT_NAME: str = "AI-Powered Ride-Sharing System"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = "sqlite:///:memory:"  # Default in-memory SQLite database
    
    # Redis (for caching and WebSocket)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Google Maps / OpenStreetMap API Key
    MAPS_API_KEY: Optional[str] = None
    
    # Payment Integration
    PAYMENT_API_KEY: Optional[str] = None
    PAYMENT_API_SECRET: Optional[str] = None
    
    # AI Model Settings
    RIDE_MATCHING_MODEL_PATH: str = "models/ride_matching_model.pkl"
    FARE_ESTIMATION_MODEL_PATH: str = "models/fare_estimation_model.pkl"
    FRAUD_DETECTION_MODEL_PATH: str = "models/fraud_detection_model.pkl"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 