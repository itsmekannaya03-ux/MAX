from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import re
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from backend.app.models.task import TaskModel

class TimetableEngine:
    def __init__(self):
        pass

    def _parse_time_str(self, time_str: str) -> datetime:
        """Parses HH:MM into a datetime object for today."""
        today = datetime.now()
        hours, minutes = map(int, time_str.split(":"))
        return today.replace(hour=hours, minute=minutes, second=0, microsecond=0)

    def _format_time_str(self, dt: datetime) -> str:
        """Formats datetime to HH:MM."""
        return dt.strftime("%H:%M")

    def get_today_tasks(self, db: Session, target_date: Optional[str] = None) -> List[TaskModel]:
        """Fetches all tasks for the given date sorted by start_time."""
        date_str = target_date or datetime.now().strftime("%Y-%m-%d")
        stmt = select(TaskModel).where(TaskModel.schedule_date == date_str).order_by(TaskModel.start_time)
        return list(db.scalars(stmt).all())

    def generate_timetable(
        self,
        db: Session,
        tasks_raw: List[str],
        completed_so_far: str = "",
        start_time_str: Optional[str] = None,
        working_hours_end: str = "22:00",
        include_breaks: bool = True,
        break_interval_minutes: int = 60,
        break_duration_minutes: int = 15,
        target_date: Optional[str] = None
    ) -> List[TaskModel]:
        """
        Creates a sequential, non-overlapping timetable from user task descriptions.
        """
        date_str = target_date or datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()

        # Determine start time: if not specified, start from next clean 5-minute interval or now
        if start_time_str:
            current_time = self._parse_time_str(start_time_str)
        else:
            minute_rounded = (now.minute // 5 + 1) * 5
            if minute_rounded >= 60:
                current_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            else:
                current_time = now.replace(minute=minute_rounded, second=0, microsecond=0)

        end_limit = self._parse_time_str(working_hours_end)

        created_tasks: List[TaskModel] = []
        minutes_accumulated_since_break = 0

        # Preserve existing completed tasks, remove pending
        existing_tasks = self.get_today_tasks(db, date_str)
        existing_completed = [t for t in existing_tasks if t.completion_status == "completed"]
        
        for t in existing_tasks:
            if t.completion_status != "completed":
                db.delete(t)
        db.commit()

        if existing_completed:
            last_end = max([self._parse_time_str(t.end_time) for t in existing_completed])
            if last_end > current_time:
                current_time = last_end

        for i, item in enumerate(tasks_raw):
            item_clean = item.strip()
            if not item_clean:
                continue

            priority = "medium"
            if "urgent" in item_clean.lower() or "high priority" in item_clean.lower() or "exam" in item_clean.lower():
                priority = "high"
            elif "quick" in item_clean.lower() or "light" in item_clean.lower() or "low" in item_clean.lower():
                priority = "low"

            duration = 60
            match_mins = re.search(r'(\d+)\s*(?:mins|min|minutes)', item_clean, re.IGNORECASE)
            match_hrs = re.search(r'(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr)', item_clean, re.IGNORECASE)
            if match_mins:
                duration = int(match_mins.group(1))
            elif match_hrs:
                duration = int(float(match_hrs.group(1)) * 60)
            elif "math" in item_clean.lower() or "python" in item_clean.lower() or "code" in item_clean.lower():
                duration = 60
            elif "review" in item_clean.lower() or "read" in item_clean.lower():
                duration = 45

            task_name = re.sub(r'\s*(?:for\s*\d+\s*(?:mins|min|minutes|hours|hour|hrs|hr)).*', '', item_clean, flags=re.IGNORECASE).strip()
            task_name = re.sub(r'\s+\d+\s*(?:mins|min|minutes|hours|hour|hrs|hr)\s*$', '', task_name, flags=re.IGNORECASE).strip()
            if not task_name:
                task_name = item_clean

            # Insert break if interval reached
            if include_breaks and minutes_accumulated_since_break >= break_interval_minutes:
                break_start = current_time
                break_end = break_start + timedelta(minutes=break_duration_minutes)
                break_task = TaskModel(
                    name="Rest & Recharge Break",
                    start_time=self._format_time_str(break_start),
                    end_time=self._format_time_str(break_end),
                    duration=break_duration_minutes,
                    priority="low",
                    description="Step away from the screen, hydrate, and stretch.",
                    completion_status="pending",
                    progress_percentage=0,
                    reminders=json.dumps([2]),
                    dependencies=json.dumps([]),
                    notes="Automatic wellness break inserted by MAX.",
                    schedule_date=date_str
                )
                db.add(break_task)
                created_tasks.append(break_task)
                current_time = break_end
                minutes_accumulated_since_break = 0

            task_start = current_time
            task_end = task_start + timedelta(minutes=duration)

            formatted_title = task_name[0].upper() + task_name[1:] if task_name else item_clean
            new_task = TaskModel(
                name=formatted_title,
                start_time=self._format_time_str(task_start),
                end_time=self._format_time_str(task_end),
                duration=duration,
                priority=priority,
                description=f"Focus block for {formatted_title}",
                completion_status="pending",
                progress_percentage=0,
                reminders=json.dumps([10, 2]),
                dependencies=json.dumps([]),
                notes="",
                schedule_date=date_str
            )
            db.add(new_task)
            created_tasks.append(new_task)

            current_time = task_end
            minutes_accumulated_since_break += duration

        db.commit()
        for t in created_tasks:
            db.refresh(t)

        return self.get_today_tasks(db, date_str)

    def adjust_schedule_nlp(
        self,
        db: Session,
        user_prompt: str,
        target_date: Optional[str] = None
    ) -> Dict[str, Any]:
        date_str = target_date or datetime.now().strftime("%Y-%m-%d")
        prompt_lower = user_prompt.lower().strip()
        tasks = self.get_today_tasks(db, date_str)

        if not tasks:
            return {
                "success": False,
                "message": "You don't have any tasks scheduled for today yet. Let me know what you want to work on first!",
                "adjusted_tasks": []
            }

        now = datetime.now()

        # 1. "I completed [task]" or "task done"
        if any(w in prompt_lower for w in ["completed", "done", "finished"]):
            matched_task = None
            for t in tasks:
                if t.completion_status != "completed" and any(word in t.name.lower() for word in prompt_lower.split() if len(word) > 3):
                    matched_task = t
                    break
            if not matched_task:
                for t in tasks:
                    if t.completion_status in ["in_progress", "pending"]:
                        matched_task = t
                        break

            if matched_task:
                matched_task.completion_status = "completed"
                matched_task.progress_percentage = 100
                db.commit()
                db.refresh(matched_task)
                return {
                    "success": True,
                    "message": f"Awesome job! I marked '{matched_task.name}' as completed. Keep this momentum going!",
                    "action": "task_completed",
                    "task_id": matched_task.id,
                    "adjusted_tasks": tasks
                }

        # 2. "Need more time"
        if "need" in prompt_lower and any(w in prompt_lower for w in ["more", "another", "extra", "additional"]):
            match_mins = re.search(r'(\d+)\s*(?:mins|min|minutes)', prompt_lower)
            extra_mins = int(match_mins.group(1)) if match_mins else 30

            target_task = None
            for t in tasks:
                if t.completion_status in ["in_progress", "pending"]:
                    target_task = t
                    break

            if target_task:
                end_dt = self._parse_time_str(target_task.end_time) + timedelta(minutes=extra_mins)
                target_task.end_time = self._format_time_str(end_dt)
                target_task.duration += extra_mins
                self._shift_subsequent_tasks(tasks, target_task, extra_mins)
                db.commit()

                return {
                    "success": True,
                    "message": f"Extended '{target_task.name}' by {extra_mins} minutes (now ends at {target_task.end_time}). I shifted remaining tasks accordingly.",
                    "action": "extended_task",
                    "adjusted_tasks": tasks
                }

        # 3. "Go outside for one hour" / "Take a break"
        if any(w in prompt_lower for w in ["go outside", "errand", "break", "leave", "step out"]):
            match_mins = re.search(r'(\d+)\s*(?:mins|min|minutes)', prompt_lower)
            match_hrs = re.search(r'(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr)', prompt_lower)
            if match_mins:
                break_mins = int(match_mins.group(1))
            elif match_hrs:
                break_mins = int(float(match_hrs.group(1)) * 60)
            elif "one hour" in prompt_lower or "1 hour" in prompt_lower:
                break_mins = 60
            else:
                break_mins = 30

            break_start = now
            break_end = break_start + timedelta(minutes=break_mins)

            new_break = TaskModel(
                name="Personal Commitment / Break",
                start_time=self._format_time_str(break_start),
                end_time=self._format_time_str(break_end),
                duration=break_mins,
                priority="medium",
                description="User requested break / outside time",
                completion_status="in_progress",
                progress_percentage=0,
                reminders=json.dumps([5]),
                dependencies=json.dumps([]),
                notes="Inserted dynamically by user request.",
                schedule_date=date_str
            )
            db.add(new_break)

            for t in tasks:
                if t.completion_status == "pending" and self._parse_time_str(t.start_time) < break_end:
                    s_dt = self._parse_time_str(t.start_time) + timedelta(minutes=break_mins)
                    e_dt = self._parse_time_str(t.end_time) + timedelta(minutes=break_mins)
                    t.start_time = self._format_time_str(s_dt)
                    t.end_time = self._format_time_str(e_dt)

            db.commit()
            updated_tasks = self.get_today_tasks(db, date_str)
            return {
                "success": True,
                "message": f"Got it! I added a {break_mins}-minute break until {self._format_time_str(break_end)} and shifted your remaining tasks.",
                "action": "inserted_break",
                "adjusted_tasks": updated_tasks
            }

        # 4. "Move [task] to [time]"
        if "move" in prompt_lower or "reschedule" in prompt_lower or "shift" in prompt_lower:
            match_time = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', prompt_lower)
            target_task = None
            for t in tasks:
                if any(w in t.name.lower() for w in prompt_lower.split() if len(w) > 3):
                    target_task = t
                    break
            
            if target_task:
                new_start_str = "18:00" if "evening" in prompt_lower else "14:00" if "afternoon" in prompt_lower else None
                if match_time and not new_start_str:
                    raw_t = match_time.group(1).strip()
                    try:
                        if ":" in raw_t:
                            parts = raw_t.split(":")
                            new_start_str = f"{int(parts[0]):02d}:{int(parts[1]):02d}"
                        else:
                            new_start_str = f"{int(raw_t):02d}:00"
                    except Exception:
                        new_start_str = "18:00"

                if new_start_str:
                    new_start_dt = self._parse_time_str(new_start_str)
                    new_end_dt = new_start_dt + timedelta(minutes=target_task.duration)
                    target_task.start_time = self._format_time_str(new_start_dt)
                    target_task.end_time = self._format_time_str(new_end_dt)
                    db.commit()
                    updated_tasks = self.get_today_tasks(db, date_str)
                    return {
                        "success": True,
                        "message": f"Moved '{target_task.name}' to start at {target_task.start_time}.",
                        "action": "moved_task",
                        "adjusted_tasks": updated_tasks
                    }

        # 5. "Don't want to study [task]"
        if any(w in prompt_lower for w in ["don't want to", "dont want to", "cancel", "remove", "skip"]):
            target_task = None
            for t in tasks:
                if any(w in t.name.lower() for w in prompt_lower.split() if len(w) > 3):
                    target_task = t
                    break
            if target_task:
                target_task.completion_status = "skipped"
                db.commit()
                return {
                    "success": True,
                    "message": f"Skipped '{target_task.name}' for today. Your schedule is updated.",
                    "action": "skipped_task",
                    "adjusted_tasks": tasks
                }

        return {
            "success": True,
            "message": f"I reviewed your request: '{user_prompt}'. Everything is balanced and your current timetable is active.",
            "action": "no_change",
            "adjusted_tasks": tasks
        }

    def _shift_subsequent_tasks(self, tasks: List[TaskModel], from_task: TaskModel, shift_minutes: int):
        from_end = self._parse_time_str(from_task.end_time)
        for t in tasks:
            if t.id != from_task.id and t.completion_status != "completed":
                t_start = self._parse_time_str(t.start_time)
                if t_start >= (from_end - timedelta(minutes=shift_minutes)):
                    new_start = t_start + timedelta(minutes=shift_minutes)
                    new_end = self._parse_time_str(t.end_time) + timedelta(minutes=shift_minutes)
                    t.start_time = self._format_time_str(new_start)
                    t.end_time = self._format_time_str(new_end)

timetable_engine = TimetableEngine()
