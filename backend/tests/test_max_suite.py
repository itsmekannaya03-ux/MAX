import sys
import unittest
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.database import init_db, SessionLocal
from backend.app.models.task import TaskModel
from backend.app.models.memory import MemoryModel
from backend.app.services.timetable_engine import timetable_engine
from backend.app.services.command_engine import command_engine
from backend.app.services.memory_engine import memory_engine
from backend.app.services.productivity_engine import productivity_engine
from backend.app.services.learning_engine import learning_engine
from backend.app.services.desktop_engine import desktop_engine
from backend.app.services.voice_engine import voice_engine
import asyncio

class TestMAXAssistant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_timetable_generation(self):
        """Test intelligent timetable generation with automatic breaks and priorities."""
        tasks = timetable_engine.generate_timetable(
            db=self.db,
            tasks_raw=["Urgent: Complete Python project 60 mins", "Study Calculus 45 mins", "Light reading 30 mins"],
            working_hours_end="22:00",
            include_breaks=True,
            break_interval_minutes=60,
            break_duration_minutes=15
        )
        self.assertGreaterEqual(len(tasks), 3)
        # Check priority detection
        task_names = [t.name for t in tasks]
        self.assertTrue(any("Python" in n for n in task_names))
        python_task = next(t for t in tasks if "Python" in t.name)
        self.assertEqual(python_task.priority, "high")

    def test_02_dynamic_rescheduling_extend(self):
        """Test extending an active task by 30 minutes."""
        res = timetable_engine.adjust_schedule_nlp(
            db=self.db,
            user_prompt="I need another 30 minutes"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["action"], "extended_task")

    def test_03_dynamic_rescheduling_break(self):
        """Test inserting a break and shifting remaining tasks."""
        res = timetable_engine.adjust_schedule_nlp(
            db=self.db,
            user_prompt="I need to go outside for 1 hour"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["action"], "inserted_break")

    def test_04_dynamic_rescheduling_completed(self):
        """Test marking a task completed through natural language."""
        res = timetable_engine.adjust_schedule_nlp(
            db=self.db,
            user_prompt="I completed my python task"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["action"], "task_completed")

    def test_05_command_engine_greetings_and_status(self):
        """Test status queries and natural language command parsing."""
        res = asyncio.run(
            command_engine.process_user_input(self.db, "MAX, what should I do right now?")
        )
        self.assertTrue(len(res.reply) > 0)
        self.assertEqual(res.action_type, "task_status")

    def test_06_command_engine_remember_fact(self):
        """Test storing memories through conversation."""
        res = asyncio.run(
            command_engine.process_user_input(self.db, "MAX, remember that my final exam is on December 15")
        )
        self.assertEqual(res.action_type, "memory_saved")
        
        # Verify in memory table
        mems = memory_engine.get_all_memories(self.db)
        self.assertTrue(any("December 15" in m.value for m in mems))

    def test_07_learning_engine_explanation(self):
        """Test AI Teacher structured concept explanation."""
        lesson = asyncio.run(
            learning_engine.explain_topic("Binary Search", user_level="beginner")
        )
        self.assertEqual(lesson.topic, "Binary Search")
        self.assertTrue(len(lesson.everyday_analogy) > 0)
        self.assertTrue(len(lesson.breakdown_steps) > 0)

    def test_08_learning_engine_quiz(self):
        """Test quiz generation and grading."""
        quiz = asyncio.run(
            learning_engine.generate_quiz(self.db, "Data Structures", num_questions=2)
        )
        self.assertEqual(len(quiz.questions), 2)
        
        # Submit answers
        answers = [q.correct_option_index for q in quiz.questions]
        result = learning_engine.submit_quiz(self.db, quiz.session_id, answers)
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["percentage"], 100)

    def test_09_productivity_and_emergency_stop(self):
        """Test active window tracking and emergency stop."""
        win_info = productivity_engine.get_active_window_info()
        self.assertIn("app", win_info)
        self.assertIn("title", win_info)

        # Trigger emergency stop
        productivity_engine.emergency_stop()
        self.assertFalse(productivity_engine.monitoring_enabled)
        self.assertFalse(productivity_engine.camera_permitted)
        self.assertFalse(productivity_engine.camera_active)

    def test_10_desktop_diagnostics(self):
        """Test non-destructive system diagnostics."""
        diag = desktop_engine.get_system_diagnostics()
        self.assertIn("os", diag)
        self.assertIn("memory_used_gb", diag)
        self.assertIn("cpu_percent", diag)
        self.assertIn("current_time", diag)

    def test_11_voice_cleaner(self):
        """Test speech text preparation removing markdown and URLs."""
        raw = "Here is **bold** text and `inline_code` with a [link](http://example.com) and ```def code(): pass```."
        cleaned = voice_engine.prepare_speech_text(raw)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("http://", cleaned)
        self.assertIn("bold text and inline_code", cleaned)

if __name__ == "__main__":
    unittest.main()
