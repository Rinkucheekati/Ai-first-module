from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ""
    
    # Application
    APP_NAME: str = "AI First CRM HCP Module"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: any) -> List[str]:
        """Parse CORS origins from comma-separated or space-separated string"""
        if isinstance(v, str):
            if "," in v:
                return [origin.strip() for origin in v.split(",")]
            else:
                return [origin.strip() for origin in v.split()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
