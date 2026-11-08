import time
import ctypes
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import psutil
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.models.productivity import ProductivityLogModel

# Win32 user32 for idle time & active window
try:
    import win32gui
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

class ProductivityEngine:
    def __init__(self):
        self.monitoring_enabled = settings.ACTIVITY_MONITOR_ENABLED
        self.camera_permitted = settings.ALLOW_WEBCAM_MONITORING
        self.camera_active = False
        self.focus_mode_active = False
        self.last_check_in_time = 0
        self.consecutive_unanswered_checkins = 0
        self.last_snapshot_presence = False

    def get_idle_duration_seconds(self) -> int:
        """Returns seconds since last keyboard or mouse input on Windows."""
        try:
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
                millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
                return int(millis / 1000.0)
        except Exception:
            pass
        return 0

    def get_active_window_info(self) -> Dict[str, str]:
        """Returns current foreground window title and executable process name."""
        if not HAS_WIN32:
            return {"title": "System Active", "app": "desktop"}
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return {"title": "Desktop / Lock Screen", "app": "explorer.exe"}
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                proc = psutil.Process(pid)
                app_name = proc.name()
            except Exception:
                app_name = "unknown"
            return {"title": title or "Background Window", "app": app_name}
        except Exception as e:
            return {"title": "Active Window", "app": "system"}

    def is_on_task(self, current_task_name: Optional[str], active_app: str, window_title: str) -> bool:
        """Compares foreground activity with the current scheduled task name."""
        if not current_task_name:
            return True
        task_lower = current_task_name.lower()
        title_lower = window_title.lower()
        app_lower = active_app.lower()

        # If user is in break task, browsing or resting is fine
        if "break" in task_lower or "rest" in task_lower:
            return True

        # Check positive keywords
        if any(w in title_lower or w in app_lower for w in task_lower.split() if len(w) > 3):
            return True

        # Common development tools
        if any(k in task_lower for k in ["code", "python", "programming", "javascript", "developer"]):
            if any(dev in app_lower or dev in title_lower for dev in ["code", "pycharm", "cursor", "antigravity", "terminal", "powershell", "cmd"]):
                return True

        # Common study/reading tools
        if any(k in task_lower for k in ["math", "study", "read", "science", "history"]):
            if any(tool in app_lower or tool in title_lower for tool in ["pdf", "acrobat", "chrome", "edge", "notepad", "word", "anki"]):
                return True

        return False

    async def capture_webcam_snapshot_check(self) -> bool:
        """
        Captures a brief snapshot ONLY if user explicitly enabled it.
        Strict privacy:
        - Never saves image to disk.
        - Analyzes basic presence (frame variance or face haar cascade).
        - Immediately disposes frame from memory.
        """
        if not self.camera_permitted or not self.monitoring_enabled:
            self.camera_active = False
            return False

        try:
            import cv2
            self.camera_active = True
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.camera_active = False
                return False

            ret, frame = cap.read()
            cap.release()
            self.camera_active = False

            if not ret or frame is None:
                return False

            # Check basic brightness/motion presence without storing anything
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            variance = gray.var()
            self.last_snapshot_presence = variance > 20.0
            return self.last_snapshot_presence
        except Exception as e:
            self.camera_active = False
            return False

    def generate_check_in(
        self,
        current_task_name: Optional[str],
        active_app: str,
        window_title: str,
        is_idle: bool
    ) -> Dict[str, Any]:
        """
        Generates an intelligent check-in if user appears distracted or idle during a task.
        Never locks computer; asks gently.
        """
        now = time.time()
        # Minimum 5 minutes between proactive check-in popups
        if now - self.last_check_in_time < 300:
            return {"prompt_needed": False}

        on_task = self.is_on_task(current_task_name, active_app, window_title)

        if current_task_name and not on_task and not is_idle:
            self.last_check_in_time = now
            return {
                "prompt_needed": True,
                "current_task_name": current_task_name,
                "question": f"You scheduled '{current_task_name}' right now, but I noticed you're currently in {active_app}. Are you working on '{current_task_name}'?",
                "suggested_actions": ["Yes, I am working on it", "No, I got distracted", "Need to reschedule"]
            }

        if current_task_name and is_idle:
            self.last_check_in_time = now
            return {
                "prompt_needed": True,
                "current_task_name": current_task_name,
                "question": f"It looks like you've been away from your computer for a bit. Are you still working on '{current_task_name}' or taking a quick break?",
                "suggested_actions": ["Still working", "Taking a break", "Completed early"]
            }

        return {"prompt_needed": False}

    def emergency_stop(self):
        """Immediately halts all monitoring, webcam access, and focus locks."""
        self.monitoring_enabled = False
        self.camera_permitted = False
        self.camera_active = False
        self.focus_mode_active = False

    def log_productivity_tick(
        self,
        db: Session,
        current_task_id: Optional[str] = None,
        current_task_name: Optional[str] = None
    ) -> ProductivityLogModel:
        idle_secs = self.get_idle_duration_seconds()
        is_idle = idle_secs >= settings.IDLE_THRESHOLD_SECONDS
        win_info = self.get_active_window_info()
        on_task = self.is_on_task(current_task_name, win_info["app"], win_info["title"])

        log_entry = ProductivityLogModel(
            active_app=win_info["app"],
            window_title=win_info["title"][:250],
            is_idle=is_idle,
            idle_duration_seconds=idle_secs,
            camera_present=self.last_snapshot_presence,
            current_task_id=current_task_id,
            on_task=on_task
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

productivity_engine = ProductivityEngine()
