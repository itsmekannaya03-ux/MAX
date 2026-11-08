from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from backend.app.models.memory import MemoryModel
from backend.app.schemas.memory import MemoryCreate, MemoryUpdate

class MemoryEngine:
    def __init__(self):
        pass

    def get_all_memories(
        self,
        db: Session,
        category: Optional[str] = None
    ) -> List[MemoryModel]:
        stmt = select(MemoryModel)
        if category:
            stmt = stmt.where(MemoryModel.category == category)
        stmt = stmt.order_by(MemoryModel.category, MemoryModel.updated_at.desc())
        return list(db.scalars(stmt).all())

    def add_or_update_memory(
        self,
        db: Session,
        category: str,
        key: str,
        value: str,
        confidence: float = 1.0,
        source: str = "user_explicit"
    ) -> MemoryModel:
        stmt = select(MemoryModel).where(MemoryModel.category == category, MemoryModel.key == key)
        existing = db.scalars(stmt).first()

        if existing:
            existing.value = value
            existing.confidence = confidence
            existing.source = source
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_mem = MemoryModel(
                category=category,
                key=key,
                value=value,
                confidence=confidence,
                source=source
            )
            db.add(new_mem)
            db.commit()
            db.refresh(new_mem)
            return new_mem

    def delete_memory(self, db: Session, memory_id: int) -> bool:
        stmt = delete(MemoryModel).where(MemoryModel.id == memory_id)
        result = db.execute(stmt)
        db.commit()
        return result.rowcount > 0

    def search_memories(self, db: Session, query: str) -> List[MemoryModel]:
        query_lower = f"%{query.lower()}%"
        stmt = select(MemoryModel).where(
            (MemoryModel.key.ilike(query_lower)) | (MemoryModel.value.ilike(query_lower))
        )
        return list(db.scalars(stmt).all())

    def get_context_summary_for_ai(self, db: Session) -> str:
        memories = self.get_all_memories(db)
        if not memories:
            return "No previous memories stored yet."

        grouped: Dict[str, List[str]] = {}
        for m in memories:
            grouped.setdefault(m.category, []).append(f"- {m.key}: {m.value}")

        lines = ["Stored User Context:"]
        for cat, items in grouped.items():
            lines.append(f"[{cat.upper()}]")
            lines.extend(items)
        return "\n".join(lines)

memory_engine = MemoryEngine()
