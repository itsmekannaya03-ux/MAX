import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.schemas.chat import ChatResponse
from backend.app.services.ai_service import ai_service
from backend.app.services.timetable_engine import timetable_engine
from backend.app.services.learning_engine import learning_engine
from backend.app.services.search_engine import search_engine
from backend.app.services.memory_engine import memory_engine
from backend.app.services.productivity_engine import productivity_engine
from backend.app.services.voice_engine import voice_engine

class CommandEngine:
    def __init__(self):
        pass

    async def process_user_input(
        self,
        db: Session,
        user_message: str,
        context_date: Optional[str] = None
    ) -> ChatResponse:
        clean_input = user_message.strip()
        lower_input = clean_input.lower()

        stripped = re.sub(r'^(?:hey\s+max[,:]?|max[,:]?)\s*', '', lower_input).strip()

        # 1. TIMETABLE ADJUSTMENT
        if any(w in stripped for w in ["completed", "done with", "finished", "need another", "need more time", "go outside", "break for", "move my", "shift my", "cancel my"]):
            adj_res = timetable_engine.adjust_schedule_nlp(db, stripped, context_date)
            reply_text = adj_res["message"]
            speech = voice_engine.prepare_speech_text(reply_text)
            return ChatResponse(
                reply=reply_text,
                speech_text=speech,
                action_type="timetable_adjusted",
                action_payload={"details": adj_res}
            )

        # 2. CREATE TIMETABLE
        if any(w in stripped for w in ["create my timetable", "schedule my day", "make a schedule", "plan my day"]) or \
           ("have to" in stripped and any(task_word in stripped for task_word in ["study", "complete", "practice", "code", "work"])):
            
            raw_tasks = re.split(r'[,;]|\band also\b|\band\b|\bthen\b', stripped)
            parsed_tasks = []
            for t in raw_tasks:
                t_sub = re.sub(r'^(?:i have to|i need to|create my timetable for|schedule|study|work on)\s*', '', t.strip(), flags=re.IGNORECASE)
                if len(t_sub) > 2 and t_sub not in ["today", "please"]:
                    parsed_tasks.append(t_sub)

            if not parsed_tasks:
                parsed_tasks = ["Core Learning Session", "Practice & Problem Solving", "Daily Review"]

            tasks = timetable_engine.generate_timetable(
                db=db,
                tasks_raw=parsed_tasks,
                target_date=context_date
            )
            reply_text = (
                f"I have crafted your personalized timetable with {len(tasks)} balanced blocks, including strategic rest breaks! "
                f"You can view the full schedule on your timetable dashboard or adjust it anytime."
            )
            speech = voice_engine.prepare_speech_text(reply_text)
            return ChatResponse(
                reply=reply_text,
                speech_text=speech,
                action_type="timetable_created",
                action_payload={"task_count": len(tasks)}
            )

        # 3. WHAT SHOULD I DO RIGHT NOW?
        if any(w in stripped for w in ["what should i do", "what's next", "whats next", "current task"]):
            tasks = timetable_engine.get_today_tasks(db, context_date)
            now_str = datetime.now().strftime("%H:%M")
            active_task = None
            next_task = None

            for i, t in enumerate(tasks):
                if t.start_time <= now_str <= t.end_time and t.completion_status != "completed":
                    active_task = t
                    if i + 1 < len(tasks):
                        next_task = tasks[i+1]
                    break
                elif t.start_time > now_str and not next_task and t.completion_status != "completed":
                    next_task = t

            if active_task:
                reply_text = f"Your current scheduled task is '{active_task.name}' (until {active_task.end_time}). Priority: {active_task.priority.upper()}."
                if next_task:
                    reply_text += f" Next up after this: '{next_task.name}' at {next_task.start_time}."
            elif next_task:
                reply_text = f"You are currently between scheduled tasks. Your next upcoming task is '{next_task.name}' starting at {next_task.start_time}."
            elif tasks:
                completed = [t for t in tasks if t.completion_status == "completed"]
                reply_text = f"You have wrapped up all tasks scheduled for today! ({len(completed)}/{len(tasks)} completed). Fantastic work!"
            else:
                reply_text = "You don't have any tasks scheduled for today yet. Tell me what you'd like to achieve and I will build your timetable."

            speech = voice_engine.prepare_speech_text(reply_text)
            return ChatResponse(
                reply=reply_text,
                speech_text=speech,
                action_type="task_status",
                action_payload={"current_task": active_task.name if active_task else None}
            )

        # 4. TEACH / EXPLAIN TOPIC
        if any(w in stripped for w in ["explain", "teach me", "what is", "how does", "tutorial on"]) and not stripped.startswith("search"):
            match_topic = re.sub(r'^(?:explain|teach me|tell me about|what is|how does)\s*', '', stripped, flags=re.IGNORECASE)
            match_topic = re.sub(r'\s*(?:like i\'m a beginner|in simple terms|for beginners|simply).*', '', match_topic, flags=re.IGNORECASE).strip()
            if not match_topic:
                match_topic = stripped

            lesson = await learning_engine.explain_topic(topic=match_topic, user_level="beginner")
            steps_str = "\n".join([f"- {s}" for s in lesson.breakdown_steps])
            reply_text = (
                f"### 🎓 Learning: {lesson.topic}\n\n"
                f"**The Big Idea:** {lesson.concept_summary}\n\n"
                f"**Everyday Analogy:** {lesson.everyday_analogy}\n\n"
                f"**Core Steps:**\n{steps_str}\n\n"
                f"**In Practice:**\n{lesson.practical_code_or_example}\n\n"
                f"**Quick Check:** {lesson.comprehension_check}"
            )
            speech = f"Here is how {lesson.topic} works in simple terms. {lesson.everyday_analogy} {lesson.concept_summary}"
            return ChatResponse(
                reply=reply_text,
                speech_text=voice_engine.prepare_speech_text(speech),
                action_type="quiz_or_lesson",
                action_payload=lesson.model_dump()
            )

        # 5. SEARCH THE WEB
        if stripped.startswith("search") or "look up" in stripped:
            query = re.sub(r'^(?:search for|search the web for|search|look up)\s*', '', stripped, flags=re.IGNORECASE).strip()
            search_res = await search_engine.search(query=query)
            reply_text = (
                f"### 🌐 Web Knowledge: '{query}'\n\n"
                f"{search_res.summary}\n\n"
                f"**Sources Found:**\n" +
                "\n".join([f"- [{r.title}]({r.link}): {r.snippet[:120]}..." for r in search_res.results[:3]])
            )
            speech = voice_engine.prepare_speech_text(search_res.summary)
            return ChatResponse(
                reply=reply_text,
                speech_text=speech,
                action_type="search_result",
                action_payload=search_res.model_dump()
            )

        # 6. SUMMARIZE ACHIEVEMENTS
        if any(w in stripped for w in ["summarize what i achieved", "daily summary", "what did i do today", "summary of today"]):
            tasks = timetable_engine.get_today_tasks(db, context_date)
            completed = [t for t in tasks if t.completion_status == "completed"]
            pending = [t for t in tasks if t.completion_status == "pending"]
            in_prog = [t for t in tasks if t.completion_status == "in_progress"]
            total = len(tasks)
            pct = int((len(completed) / total * 100)) if total else 0

            completed_names = ", ".join([f"'{t.name}'" for t in completed]) if completed else "None yet"
            reply_text = (
                f"### 📊 Today's Executive Summary\n\n"
                f"- **Completion Score:** {pct}% ({len(completed)} of {total} tasks)\n"
                f"- **Accomplishments:** {completed_names}\n"
                f"- **In Progress:** {len(in_prog)} task(s)\n"
                f"- **Remaining:** {len(pending)} task(s)\n\n"
                f"Keep up the momentum! Let me know if you'd like to prepare tomorrow's schedule."
            )
            speech = f"Today you have completed {len(completed)} out of {total} planned tasks, reaching a completion score of {pct} percent."
            return ChatResponse(
                reply=reply_text,
                speech_text=speech,
                action_type="daily_summary",
                action_payload={"completion_percentage": pct, "completed_count": len(completed)}
            )

        # 7. REMEMBER PREFERENCE OR GOAL
        if "remember" in stripped or "note that" in stripped:
            orig_stripped = re.sub(r'^(?:hey\s+max[,:]?|max[,:]?)\s*', '', clean_input, flags=re.IGNORECASE).strip()
            fact = re.sub(r'^(?:remember that|remember|note that|keep in mind)\s*', '', orig_stripped, flags=re.IGNORECASE).strip()
            cat = "goal" if "goal" in fact.lower() else "preference" if ("prefer" in fact.lower() or "like" in fact.lower()) else "routine"
            mem = memory_engine.add_or_update_memory(
                db=db,
                category=cat,
                key=fact[:40],
                value=fact,
                source="user_explicit"
            )
            reply_text = f"Got it! I have saved this to your persistent memory under **{cat.upper()}**: '{fact}'."
            speech = f"I've saved that to your memory."
            return ChatResponse(
                reply=reply_text,
                speech_text=speech,
                action_type="memory_saved",
                action_payload={"category": cat, "key": fact[:40]}
            )

        # 8. GENERAL AI CONVERSATION
        context_memories = memory_engine.get_context_summary_for_ai(db)
        ai_reply = await ai_service.generate_response(
            messages=[
                {"role": "user", "content": f"{context_memories}\n\nUser: {clean_input}"}
            ]
        )
        speech = voice_engine.prepare_speech_text(ai_reply)
        return ChatResponse(
            reply=ai_reply,
            speech_text=speech,
            action_type="chat"
        )

command_engine = CommandEngine()
