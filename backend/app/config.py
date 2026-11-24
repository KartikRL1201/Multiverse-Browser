import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Multiverse Browser"
    VERSION: str = "0.1.0-mvp"
    BACKEND_PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Mock Shop URL base
    MOCK_SHOP_BASE_URL: str = os.getenv("MOCK_SHOP_BASE_URL", "http://localhost:8000/mock")
    
    # Sponsors & AI Configuration
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "multiverse-browser-evidence")
    
    # Safety Guardrails
    MAX_STEPS_PER_UNIVERSE: int = 15
    TIMEOUT_SECONDS_PER_UNIVERSE: int = 60
    READ_ONLY_MODE: bool = True

settings = Settings()
