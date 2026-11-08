from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from datetime import datetime, timezone
from backend.app.database import Base

class MemoryModel(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False) # preference, goal, routine, learning_history, project, productivity_pattern, note
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    source = Column(String(30), default="user_explicit") # user_explicit, system_inferred
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

