from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import List, Optional
from datetime import datetime
from backend.app.database import get_db
from backend.app.models.task import TaskModel
from backend.app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse,
    TimetableGenerateRequest, TimetableAdjustRequest
)
from backend.app.services.timetable_engine import timetable_engine
import json

router = APIRouter(prefix="/api/timetable", tags=["Timetable Engine"])

@router.get("", response_model=List[TaskResponse])
def get_timetable(date: Optional[str] = None, db: Session = Depends(get_db)):
    tasks = timetable_engine.get_today_tasks(db, target_date=date)
    out = []
    for t in tasks:
        rem = json.loads(t.reminders) if t.reminders else []
        dep = json.loads(t.dependencies) if t.dependencies else []
        out.append(TaskResponse(
            id=t.id,
            name=t.name,
            start_time=t.start_time,
            end_time=t.end_time,
            duration=t.duration,
            priority=t.priority,
            description=t.description or "",
            completion_status=t.completion_status,
            progress_percentage=t.progress_percentage,
            reminders=rem,
            dependencies=dep,
            notes=t.notes or "",
            schedule_date=t.schedule_date,
            created_at=t.created_at,
            updated_at=t.updated_at
        ))
    return out

@router.post("/generate", response_model=List[TaskResponse])
def generate_timetable(req: TimetableGenerateRequest, db: Session = Depends(get_db)):
    tasks = timetable_engine.generate_timetable(
        db=db,
        tasks_raw=req.tasks_to_accomplish,
        completed_so_far=req.completed_so_far or "",
        start_time_str=req.working_hours_start,
        working_hours_end=req.working_hours_end or "22:00",
        include_breaks=req.include_breaks,
        break_interval_minutes=req.break_interval_minutes,
        break_duration_minutes=req.break_duration_minutes
    )
    return [
        TaskResponse(
            id=t.id,
            name=t.name,
            start_time=t.start_time,
            end_time=t.end_time,
            duration=t.duration,
            priority=t.priority,
            description=t.description or "",
            completion_status=t.completion_status,
            progress_percentage=t.progress_percentage,
            reminders=json.loads(t.reminders) if t.reminders else [],
            dependencies=json.loads(t.dependencies) if t.dependencies else [],
            notes=t.notes or "",
            schedule_date=t.schedule_date
        ) for t in tasks
    ]

@router.post("/adjust")
def adjust_timetable(req: TimetableAdjustRequest, db: Session = Depends(get_db)):
    return timetable_engine.adjust_schedule_nlp(
        db=db,
        user_prompt=req.user_prompt,
        target_date=req.target_date
    )

@router.post("/task", response_model=TaskResponse)
def create_task(req: TaskCreate, db: Session = Depends(get_db)):
    new_task = TaskModel(
        name=req.name,
        start_time=req.start_time,
        end_time=req.end_time,
        duration=req.duration,
        priority=req.priority,
        description=req.description or "",
        completion_status=req.completion_status,
        progress_percentage=req.progress_percentage,
        reminders=json.dumps(req.reminders or []),
        dependencies=json.dumps(req.dependencies or []),
        notes=req.notes or "",
        schedule_date=req.schedule_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return TaskResponse(
        id=new_task.id,
        name=new_task.name,
        start_time=new_task.start_time,
        end_time=new_task.end_time,
        duration=new_task.duration,
        priority=new_task.priority,
        description=new_task.description or "",
        completion_status=new_task.completion_status,
        progress_percentage=new_task.progress_percentage,
        reminders=json.loads(new_task.reminders) if new_task.reminders else [],
        dependencies=json.loads(new_task.dependencies) if new_task.dependencies else [],
        notes=new_task.notes or "",
        schedule_date=new_task.schedule_date
    )

@router.put("/task/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, req: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if field in ["reminders", "dependencies"] and isinstance(val, list):
            setattr(task, field, json.dumps(val))
        else:
            setattr(task, field, val)

    db.commit()
    db.refresh(task)

    return TaskResponse(
        id=task.id,
        name=task.name,
        start_time=task.start_time,
        end_time=task.end_time,
        duration=task.duration,
        priority=task.priority,
        description=task.description or "",
        completion_status=task.completion_status,
        progress_percentage=task.progress_percentage,
        reminders=json.loads(task.reminders) if task.reminders else [],
        dependencies=json.loads(task.dependencies) if task.dependencies else [],
        notes=task.notes or "",
        schedule_date=task.schedule_date
    )

@router.delete("/task/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    count = db.query(TaskModel).filter(TaskModel.id == task_id).delete()
    db.commit()
    if count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": f"Task {task_id} deleted."}
