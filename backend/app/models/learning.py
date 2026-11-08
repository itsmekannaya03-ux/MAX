from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime, timezone
from backend.app.database import Base

class LearningSessionModel(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(200), nullable=False)
    level = Column(String(50), default="beginner") # beginner, intermediate, advanced
    summary = Column(Text, default="")
    quiz_data = Column(Text, default="[]") # JSON list of questions, options, answers, explanations
    quiz_score = Column(Integer, nullable=True)
    quiz_total = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

