from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductivityStatusResponse(BaseModel):
    monitoring_enabled: bool
    camera_permitted: bool
    camera_active: bool
    active_window: str
    active_app: str
    is_idle: bool
    idle_seconds: int
    focus_mode_active: bool
    current_task_id: Optional[str] = None
    current_task_name: Optional[str] = None
    today_focus_minutes: int
    completion_rate_percentage: int

class ProductivityCheckInResponse(BaseModel):
    prompt_needed: bool
    question: Optional[str] = None
    current_task_name: Optional[str] = None
    suggested_actions: List[str] = []

class CheckInAnswerRequest(BaseModel):
    working_on_task: bool
    actual_activity: Optional[str] = None
    reason: Optional[str] = None
    adjust_schedule: bool = False

