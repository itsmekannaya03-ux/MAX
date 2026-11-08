from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MemoryBase(BaseModel):
    category: str
    key: str
    value: str
    confidence: float = 1.0
    source: str = "user_explicit"

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(BaseModel):
    category: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    confidence: Optional[float] = None
    source: Optional[str] = None

class MemoryResponse(MemoryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

