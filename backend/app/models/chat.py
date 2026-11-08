from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime, timezone
from backend.app.database import Base

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(20), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(30), default="text") # text, command, schedule_update, check_in, quiz, search_result
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

