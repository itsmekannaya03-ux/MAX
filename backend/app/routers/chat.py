from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import List, Dict, Any
from backend.app.database import get_db
from backend.app.schemas.chat import ChatRequest, ChatResponse, ConfirmationActionRequest
from backend.app.models.chat import ChatMessageModel
from backend.app.services.command_engine import command_engine

router = APIRouter(prefix="/api/chat", tags=["Chat & Commands"])

@router.post("", response_model=ChatResponse)
async def chat_message(req: ChatRequest, db: Session = Depends(get_db)):
    user_msg = ChatMessageModel(
        role="user",
        content=req.message,
        message_type="voice" if req.voice_input else "text"
    )
    db.add(user_msg)
    db.commit()

    response = await command_engine.process_user_input(
        db=db,
        user_message=req.message,
        context_date=req.context_date
    )

    bot_msg = ChatMessageModel(
        role="assistant",
        content=response.reply,
        message_type=response.action_type
    )
    db.add(bot_msg)
    db.commit()

    return response

@router.get("/history")
def get_chat_history(limit: int = 50, db: Session = Depends(get_db)):
    stmt = select(ChatMessageModel).order_by(ChatMessageModel.created_at.desc()).limit(limit)
    messages = list(db.scalars(stmt).all())
    messages.reverse()
    return [{"id": m.id, "role": m.role, "content": m.content, "message_type": m.message_type, "created_at": m.created_at} for m in messages]

@router.delete("/history")
def clear_chat_history(db: Session = Depends(get_db)):
    db.query(ChatMessageModel).delete()
    db.commit()
    return {"status": "success", "message": "Chat history cleared."}
