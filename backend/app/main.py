import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import select

from backend.app.config import settings
from backend.app.database import init_db, SessionLocal
from backend.app.models.task import TaskModel
from backend.app.services.productivity_engine import productivity_engine
from backend.app.services.notification_engine import notification_engine
from backend.app.services.timetable_engine import timetable_engine

from backend.app.routers.chat import router as chat_router
from backend.app.routers.timetable import router as timetable_router
from backend.app.routers.productivity import router as productivity_router
from backend.app.routers.memory import router as memory_router
from backend.app.routers.learning import router as learning_router
from backend.app.routers.search import router as search_router
from backend.app.routers.settings import router as settings_router

# Active WebSocket connections
active_connections: Set[WebSocket] = set()

async def ws_broadcast_handler(data: dict):
    for ws in list(active_connections):
        try:
            await ws.send_json(data)
        except Exception:
            active_connections.discard(ws)

# Background scheduler task
background_task_handle = None

async def background_monitoring_and_reminders():
    """
    Continuous background loop:
    1. Checks timetable for upcoming tasks (10m and 2m reminders).
    2. Logs productivity snapshots every 60s.
    3. Triggers intelligent check-ins if off-task or idle.
    """
    notification_engine.subscribe(ws_broadcast_handler)
    reminded_keys = set()

    while True:
        try:
            await asyncio.sleep(20) # evaluate every 20 seconds
            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            now_time_str = now.strftime("%H:%M")

            with SessionLocal() as db:
                # 1. Timetable Reminders
                tasks = timetable_engine.get_today_tasks(db, today_str)
                current_active_task = None

                for t in tasks:
                    if t.completion_status in ["completed", "skipped"]:
                        continue

                    # Check current active task
                    if t.start_time <= now_time_str <= t.end_time:
                        current_active_task = t

                    # Calculate minutes until start
                    try:
                        th, tm = map(int, t.start_time.split(":"))
                        t_start_dt = now.replace(hour=th, minute=tm, second=0, microsecond=0)
                        diff_mins = int((t_start_dt - now).total_seconds() / 60)

                        if 9 <= diff_mins <= 10:
                            key = f"{t.id}_10m"
                            if key not in reminded_keys:
                                reminded_keys.add(key)
                                await notification_engine.send_desktop_notification(
                                    title="Upcoming Task in 10 Minutes",
                                    message=f"'{t.name}' is scheduled to start at {t.start_time}."
                                )

                        elif 0 <= diff_mins <= 2:
                            key = f"{t.id}_2m"
                            if key not in reminded_keys:
                                reminded_keys.add(key)
                                await notification_engine.send_desktop_notification(
                                    title="Task Starting Now",
                                    message=f"Time to start '{t.name}'! (Priority: {t.priority.upper()})"
                                )
                    except Exception:
                        pass

                # 2. Log productivity tick
                if productivity_engine.monitoring_enabled:
                    productivity_engine.log_productivity_tick(
                        db=db,
                        current_task_id=current_active_task.id if current_active_task else None,
                        current_task_name=current_active_task.name if current_active_task else None
                    )

                # 3. Optional webcam check if permitted
                if productivity_engine.camera_permitted:
                    await productivity_engine.capture_webcam_snapshot_check()

        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[BackgroundWorker] Loop exception: {e}")

import threading

def run_background_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(background_monitoring_and_reminders())
    except Exception as e:
        print(f"[BackgroundThread] {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    print("[MAX] Initializing database...")
    init_db()
    print("[MAX] Database initialized.")
    # Launch background loop in daemon thread so it never blocks anyio lifespan
    worker_thread = threading.Thread(target=run_background_loop, daemon=True)
    worker_thread.start()
    yield

app = FastAPI(
    title="MAX — My AI eXecutive Assistant",
    description="Proactive, intelligent, desktop AI companion backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for desktop webview and local client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(chat_router)
app.include_router(timetable_router)
app.include_router(productivity_router)
app.include_router(memory_router)
app.include_router(learning_router)
app.include_router(search_router)
app.include_router(settings_router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        # Send initial welcome sync
        await websocket.send_json({
            "type": "connected",
            "message": "MAX Intelligence Core connected",
            "timestamp": datetime.now().isoformat()
        })
        while True:
            data = await websocket.receive_text()
            # Can process ping or client triggers
    except WebSocketDisconnect:
        active_connections.discard(websocket)
    except Exception:
        active_connections.discard(websocket)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "MAX",
        "local_time": datetime.now().isoformat(),
        "ai_provider": settings.AI_PROVIDER,
        "monitoring_active": productivity_engine.monitoring_enabled
    }

# Mount static build files if frontend/dist exists
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("ws"):
            return None
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
