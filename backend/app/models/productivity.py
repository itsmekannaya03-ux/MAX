from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from datetime import datetime, timezone
from backend.app.database import Base

class ProductivityLogModel(Base):
    __tablename__ = "productivity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    active_app = Column(String(100), default="")
    window_title = Column(String(255), default="")
    is_idle = Column(Boolean, default=False)
    idle_duration_seconds = Column(Integer, default=0)
    camera_present = Column(Boolean, default=False)
    current_task_id = Column(String(36), nullable=True)
    on_task = Column(Boolean, default=True)
    notes = Column(Text, default="")

