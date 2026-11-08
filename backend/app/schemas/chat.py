from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    context_date: Optional[str] = None
    voice_input: bool = False

class ChatResponse(BaseModel):
    reply: str
    speech_text: Optional[str] = None
    action_type: str = "chat" # chat, timetable_created, timetable_adjusted, task_completed, quiz, search_result, system_action
    action_payload: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None

class ConfirmationActionRequest(BaseModel):
    action_id: str
    approved: bool
    payload: Optional[Dict[str, Any]] = None

