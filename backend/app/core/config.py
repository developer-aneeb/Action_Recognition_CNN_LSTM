"""
Application Configuration
Manages all settings using Pydantic Settings for type safety and validation
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # App Info
    APP_NAME: str = "Action Recognition API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "CNN-LSTM based video action recognition API"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - Frontend origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Model Configuration
    MODEL_PATH: str = str(Path(__file__).parent.parent.parent / "model" / "best_action_recognition_model.h5")
    
    # Video Processing
    NUM_FRAMES: int = 16
    FRAME_HEIGHT: int = 112
    FRAME_WIDTH: int = 112
    CHANNELS: int = 3
    
    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".mpg", ".mpeg", ".webm"]
    UPLOAD_DIR: str = str(Path(__file__).parent.parent / "uploads")
    
    # UCF11 Action Classes (in sorted order as trained)
    ACTION_CLASSES: List[str] = [
        "basketball",
        "biking", 
        "diving",
        "golf_swing",
        "horse_riding",
        "soccer_juggling",
        "swing",
        "tennis_swing",
        "trampoline_jumping",
        "volleyball_spiking",
        "walking"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create settings instance
settings = get_settings()
