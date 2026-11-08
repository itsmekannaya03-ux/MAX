from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.schemas.memory import MemoryCreate, MemoryUpdate, MemoryResponse
from backend.app.services.memory_engine import memory_engine

router = APIRouter(prefix="/api/memory", tags=["AI Memory"])

@router.get("", response_model=List[MemoryResponse])
def get_memories(category: Optional[str] = None, db: Session = Depends(get_db)):
    return memory_engine.get_all_memories(db, category)

@router.post("", response_model=MemoryResponse)
def create_or_update_memory(req: MemoryCreate, db: Session = Depends(get_db)):
    return memory_engine.add_or_update_memory(
        db=db,
        category=req.category,
        key=req.key,
        value=req.value,
        confidence=req.confidence,
        source=req.source
    )

@router.delete("/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    success = memory_engine.delete_memory(db, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    return {"status": "success", "message": f"Memory {memory_id} deleted"}

@router.get("/search", response_model=List[MemoryResponse])
def search_memories(q: str = Query(...), db: Session = Depends(get_db)):
    return memory_engine.search_memories(db, q)
