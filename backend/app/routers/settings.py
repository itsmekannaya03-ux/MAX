from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.app.config import settings, update_env_setting
from backend.app.services.desktop_engine import desktop_engine

router = APIRouter(prefix="/api/settings", tags=["Settings & Diagnostics"])

class SettingsUpdateRequest(BaseModel):
    AI_PROVIDER: Optional[str] = None
    AI_MODEL: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: Optional[str] = None
    DEFAULT_TTS_VOICE: Optional[str] = None
    DEFAULT_TTS_SPEED: Optional[float] = None
    ALLOW_WEBCAM_MONITORING: Optional[bool] = None
    ACTIVITY_MONITOR_ENABLED: Optional[bool] = None
    IDLE_THRESHOLD_SECONDS: Optional[int] = None

@router.get("")
async def get_settings():
    def mask_key(k: Optional[str]):
        if not k or len(k) < 6:
            return ""
        return k[:3] + "..." + k[-3:]

    return {
        "AI_PROVIDER": settings.AI_PROVIDER,
        "AI_MODEL": settings.AI_MODEL,
        "GEMINI_API_KEY_MASKED": mask_key(settings.GEMINI_API_KEY),
        "OPENAI_API_KEY_MASKED": mask_key(settings.OPENAI_API_KEY),
        "GROQ_API_KEY_MASKED": mask_key(settings.GROQ_API_KEY),
        "OLLAMA_BASE_URL": settings.OLLAMA_BASE_URL,
        "DEFAULT_TTS_VOICE": settings.DEFAULT_TTS_VOICE,
        "DEFAULT_TTS_SPEED": settings.DEFAULT_TTS_SPEED,
        "ALLOW_WEBCAM_MONITORING": settings.ALLOW_WEBCAM_MONITORING,
        "ACTIVITY_MONITOR_ENABLED": settings.ACTIVITY_MONITOR_ENABLED,
        "IDLE_THRESHOLD_SECONDS": settings.IDLE_THRESHOLD_SECONDS
    }

@router.post("")
async def update_settings(req: SettingsUpdateRequest):
    updates = req.model_dump(exclude_unset=True)
    for k, v in updates.items():
        if v is not None:
            update_env_setting(k, str(v))
    return {"status": "success", "message": "Settings updated successfully"}

@router.get("/diagnostics")
async def get_diagnostics():
    return desktop_engine.get_system_diagnostics()

