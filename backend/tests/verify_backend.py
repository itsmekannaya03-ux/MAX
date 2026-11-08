import sys
sys.stdout.reconfigure(line_buffering=True)
import asyncio
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from datetime import datetime

async def test_backend():
    print("Testing backend imports...")
    from backend.app.config import settings
    from backend.app.database import init_db, SessionLocal
    from backend.app.services.ai_service import ai_service
    from backend.app.services.command_engine import command_engine
    from backend.app.services.timetable_engine import timetable_engine
    from backend.app.services.productivity_engine import productivity_engine
    from backend.app.services.learning_engine import learning_engine
    from backend.app.services.search_engine import search_engine
    from backend.app.services.memory_engine import memory_engine
    from backend.app.services.desktop_engine import desktop_engine
    from backend.app.main import app

    print("Initializing database tables...")
    init_db()

    with SessionLocal() as session:
        print("1. Testing timetable generation...")
        tasks = timetable_engine.generate_timetable(
            db=session,
            tasks_raw=["Study Python OOP 45 mins", "Practice calculus 60 mins"],
            working_hours_end="22:00"
        )
        print(f"Generated {len(tasks)} tasks:")
        for t in tasks:
            print(f" - [{t.start_time} - {t.end_time}] {t.name} ({t.duration}m, {t.priority})")

        print("2. Testing natural language rescheduling...")
        res = timetable_engine.adjust_schedule_nlp(
            db=session,
            user_prompt="I need another 15 minutes"
        )
        print(f"Reschedule result: {res['message']}")

        print("3. Testing Command Engine...")
        cmd_res = await command_engine.process_user_input(
            db=session,
            user_message="MAX, what should I do right now?"
        )
        print(f"Command response: {cmd_res.reply}")

        print("4. Testing AI Teacher...")
        lesson = await learning_engine.explain_topic("Binary Search", user_level="beginner")
        print(f"Lesson topic: {lesson.topic}")
        print(f"Everyday Analogy: {lesson.everyday_analogy}")

        print("5. Testing Memory System...")
        mem = memory_engine.add_or_update_memory(
            db=session,
            category="preference",
            key="Study Environment",
            value="Prefers 50-minute pomodoros with ambient lofi music"
        )
        print(f"Saved memory: {mem.key} -> {mem.value}")

        print("6. Testing Desktop Diagnostics...")
        diag = desktop_engine.get_system_diagnostics()
        print(f"System: OS={diag['os']}, Memory={diag['memory_used_gb']}/{diag['memory_total_gb']}GB, Disk={diag['disk_percent']}%")

    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_backend())
