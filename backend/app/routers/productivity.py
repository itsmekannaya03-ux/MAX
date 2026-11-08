from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.database import get_db
from backend.app.schemas.productivity import (
    ProductivityStatusResponse, ProductivityCheckInResponse, CheckInAnswerRequest
)
from backend.app.models.productivity import ProductivityLogModel
from backend.app.models.task import TaskModel
from backend.app.services.productivity_engine import productivity_engine
from backend.app.services.timetable_engine import timetable_engine

router = APIRouter(prefix="/api/productivity", tags=["Productivity & Monitoring"])

@router.get("/status", response_model=ProductivityStatusResponse)
def get_productivity_status(db: Session = Depends(get_db)):
    win_info = productivity_engine.get_active_window_info()
    idle_secs = productivity_engine.get_idle_duration_seconds()

    now_str = datetime.now().strftime("%H:%M")
    today_str = datetime.now().strftime("%Y-%m-%d")
    tasks = timetable_engine.get_today_tasks(db, today_str)

    current_task = None
    completed_count = 0
    for t in tasks:
        if t.completion_status == "completed":
            completed_count += 1
        elif t.start_time <= now_str <= t.end_time and not current_task:
            current_task = t

    comp_rate = int((completed_count / len(tasks)) * 100) if tasks else 0

    return ProductivityStatusResponse(
        monitoring_enabled=productivity_engine.monitoring_enabled,
        camera_permitted=productivity_engine.camera_permitted,
        camera_active=productivity_engine.camera_active,
        active_window=win_info["title"],
        active_app=win_info["app"],
        is_idle=idle_secs >= 300,
        idle_seconds=idle_secs,
        focus_mode_active=productivity_engine.focus_mode_active,
        current_task_id=current_task.id if current_task else None,
        current_task_name=current_task.name if current_task else None,
        today_focus_minutes=completed_count * 50,
        completion_rate_percentage=comp_rate
    )

@router.post("/toggle-monitoring")
def toggle_monitoring(enabled: bool):
    productivity_engine.monitoring_enabled = enabled
    return {"status": "success", "monitoring_enabled": productivity_engine.monitoring_enabled}

@router.post("/toggle-camera")
def toggle_camera(permitted: bool):
    productivity_engine.camera_permitted = permitted
    if not permitted:
        productivity_engine.camera_active = False
    return {"status": "success", "camera_permitted": productivity_engine.camera_permitted}

@router.post("/emergency-stop")
def emergency_stop():
    productivity_engine.emergency_stop()
    return {"status": "emergency_stopped", "message": "All monitoring and camera access immediately disabled."}

@router.get("/check-in", response_model=ProductivityCheckInResponse)
def check_in(db: Session = Depends(get_db)):
    win_info = productivity_engine.get_active_window_info()
    idle_secs = productivity_engine.get_idle_duration_seconds()
    is_idle = idle_secs >= 300

    now_str = datetime.now().strftime("%H:%M")
    tasks = timetable_engine.get_today_tasks(db)
    current_task = next((t for t in tasks if t.start_time <= now_str <= t.end_time and t.completion_status != "completed"), None)

    checkin = productivity_engine.generate_check_in(
        current_task_name=current_task.name if current_task else None,
        active_app=win_info["app"],
        window_title=win_info["title"],
        is_idle=is_idle
    )

    return ProductivityCheckInResponse(
        prompt_needed=checkin.get("prompt_needed", False),
        question=checkin.get("question"),
        current_task_name=checkin.get("current_task_name"),
        suggested_actions=checkin.get("suggested_actions", [])
    )

@router.post("/check-in/answer")
def answer_check_in(req: CheckInAnswerRequest, db: Session = Depends(get_db)):
    if req.working_on_task:
        return {"status": "success", "message": "Great! Continuing session tracking."}
    else:
        if req.adjust_schedule:
            prompt = f"Adjust schedule: user was doing '{req.actual_activity or 'other tasks'}' instead of scheduled task."
            adj_res = timetable_engine.adjust_schedule_nlp(db, prompt)
            return {"status": "adjusted", "message": "Schedule adjusted smoothly.", "details": adj_res}
        return {"status": "noted", "message": "Understood. Let me know whenever you want to reschedule."}
