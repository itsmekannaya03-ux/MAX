from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime, timezone
import uuid
from backend.app.database import Base

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    start_time = Column(String(10), nullable=False)  # HH:MM format
    end_time = Column(String(10), nullable=False)    # HH:MM format
    duration = Column(Integer, nullable=False)       # in minutes
    priority = Column(String(20), default="medium")  # low, medium, high
    description = Column(Text, default="")
    completion_status = Column(String(30), default="pending")  # pending, in_progress, completed, skipped
    progress_percentage = Column(Integer, default=0) # 0-100
    reminders = Column(Text, default="[]")           # JSON string list of reminder minutes before start
    dependencies = Column(Text, default="[]")        # JSON string list of prerequisite task IDs or names
    notes = Column(Text, default="")
    schedule_date = Column(String(10), nullable=False) # YYYY-MM-DD
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

