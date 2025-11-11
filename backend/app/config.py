from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os


# Get the project root directory (2 levels up from this file)
# backend/app/config.py -> backend/app -> backend -> root
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    
    # Google Cloud (optional for TTS)
    google_application_credentials: str = ""
    google_cloud_project: str = ""
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Paths (relative to project root)
    storage_path: Path = PROJECT_ROOT / "backend" / "storage"
    remotion_project_path: Path = PROJECT_ROOT / "frontend" / "video"
    
    # Video Settings
    default_video_duration: int = 60
    video_fps: int = 30
    video_width: int = 1080
    video_height: int = 1920
    
    # Feature Flags
    enable_tts: bool = False  # Disabled by default
    enable_sound_effects: bool = True
    
    class Config:
        # Point to .env in project root
        env_file = str(PROJECT_ROOT / ".env")
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
