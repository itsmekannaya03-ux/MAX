from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any
from backend.app.database import get_db
from backend.app.schemas.learning import (
    LessonExplainRequest, LessonExplainResponse,
    QuizGenerateRequest, QuizResponse, QuizSubmitRequest, QuizResultResponse
)
from backend.app.models.learning import LearningSessionModel
from backend.app.services.learning_engine import learning_engine

router = APIRouter(prefix="/api/learning", tags=["AI Teacher"])

@router.post("/explain", response_model=LessonExplainResponse)
async def explain_topic(req: LessonExplainRequest):
    return await learning_engine.explain_topic(
        topic=req.topic,
        user_level=req.user_level
    )

@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(req: QuizGenerateRequest, db: Session = Depends(get_db)):
    return await learning_engine.generate_quiz(
        db=db,
        topic=req.topic,
        num_questions=req.num_questions,
        level=req.level
    )

@router.post("/quiz/submit", response_model=QuizResultResponse)
def submit_quiz(req: QuizSubmitRequest, db: Session = Depends(get_db)):
    res = learning_engine.submit_quiz(
        db=db,
        session_id=req.session_id,
        user_answers=req.answers
    )
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/history")
def get_learning_history(db: Session = Depends(get_db)):
    stmt = select(LearningSessionModel).order_by(LearningSessionModel.created_at.desc()).limit(20)
    sessions = db.scalars(stmt).all()
    return [
        {
            "id": s.id,
            "topic": s.topic,
            "level": s.level,
            "summary": s.summary,
            "quiz_score": s.quiz_score,
            "quiz_total": s.quiz_total,
            "created_at": s.created_at
        } for s in sessions
    ]
