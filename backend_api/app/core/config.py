import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Network AI Backend"
    VERSION: str = "2.0.0 (DATN Edition)"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ptit_secret_network_ai_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database (PostgreSQL with SQLite fallback)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://hoanganh:123456@localhost/network_db"
    )
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ]
    
    # Network Agent Execution Settings
    AGENT_PYTHON_EXEC: str = os.getenv("AGENT_PYTHON_EXEC", "")
    AGENT_SCRIPT_PATH: str = os.getenv("AGENT_SCRIPT_PATH", "")

settings = Settings()

