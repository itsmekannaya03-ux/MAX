import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    DEBUG: bool = True

    # AI Configuration
    AI_PROVIDER: str = "offline"  # gemini, openai, groq, ollama, offline
    AI_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Voice Configuration
    DEFAULT_TTS_VOICE: str = "en-US-JennyNeural"
    DEFAULT_TTS_SPEED: float = 1.0

    # Productivity & Privacy Configuration
    ALLOW_WEBCAM_MONITORING: bool = False
    WEBCAM_INTERVAL_SECONDS: int = 60
    ACTIVITY_MONITOR_ENABLED: bool = True
    IDLE_THRESHOLD_SECONDS: int = 300

    # Storage
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'max_assistant.db'}"

    class Config:
        env_file = str(ENV_PATH)
        extra = "allow"

settings = Settings()

def update_env_setting(key: str, value: str):
    """Safely updates or inserts a key in the .env file and in-memory settings."""
    setattr(settings, key, value)
    lines = []
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{key}={value}\n")
    
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
