from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TaskBase(BaseModel):
    name: str
    start_time: str
    end_time: str
    duration: int
    priority: str = "medium"
    description: Optional[str] = ""
    completion_status: str = "pending"
    progress_percentage: int = 0
    reminders: Optional[List[int]] = []
    dependencies: Optional[List[str]] = []
    notes: Optional[str] = ""
    schedule_date: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[int] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    completion_status: Optional[str] = None
    progress_percentage: Optional[int] = None
    reminders: Optional[List[int]] = None
    dependencies: Optional[List[str]] = None
    notes: Optional[str] = None
    schedule_date: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TimetableGenerateRequest(BaseModel):
    completed_so_far: Optional[str] = ""
    tasks_to_accomplish: List[str]
    working_hours_start: Optional[str] = None # HH:MM or None to use now
    working_hours_end: Optional[str] = "22:00"
    deadlines_and_priorities: Optional[str] = ""
    include_breaks: bool = True
    break_interval_minutes: int = 60
    break_duration_minutes: int = 15

class TimetableAdjustRequest(BaseModel):
    user_prompt: str # e.g. "I need 30 minutes break", "I completed python", "move math to 6pm"
    target_date: Optional[str] = None

