import json
import re
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.config import settings

MAX_SYSTEM_PROMPT = """You are MAX (My AI eXecutive Assistant), an elite, proactive, highly capable personal desktop AI assistant.
Your qualities:
- Friendly, articulate, practical, encouraging, and razor-sharp.
- You understand typos, incomplete sentences, colloquial speech, and the user's intent.
- You keep answers clear, structured, and helpful.
- You act as a productivity companion, scheduler, and patient teacher.
- When explaining complex ideas, you use everyday analogies, break things into steps, and avoid confusing jargon.
- When dealing with timetables, you respect deadlines, realistic time limits, and breaks.

Always respond in valid JSON when requested, or conversational text when chatting.
"""

class AIService:
    def __init__(self):
        pass

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str = MAX_SYSTEM_PROMPT,
        temperature: float = 0.7,
        force_json: bool = False
    ) -> str:
        provider = settings.AI_PROVIDER.lower()

        # Check if user has API keys configured
        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return await self._call_gemini(messages, system_instruction, temperature, force_json)
            except Exception as e:
                print(f"[AIService] Gemini API error: {e}, falling back to offline engine.")

        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return await self._call_openai(messages, system_instruction, temperature, force_json)
            except Exception as e:
                print(f"[AIService] OpenAI API error: {e}, falling back to offline engine.")

        elif provider == "groq" and settings.GROQ_API_KEY:
            try:
                return await self._call_groq(messages, system_instruction, temperature, force_json)
            except Exception as e:
                print(f"[AIService] Groq API error: {e}, falling back to offline engine.")

        elif provider == "ollama":
            try:
                return await self._call_ollama(messages, system_instruction, temperature, force_json)
            except Exception as e:
                print(f"[AIService] Ollama API error: {e}, falling back to offline engine.")

        # Fallback to local heuristic engine
        return self._local_heuristic_response(messages, force_json)

    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float,
        force_json: bool
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        body = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": temperature,
            }
        }
        if force_json:
            body["generationConfig"]["responseMimeType"] = "application/json"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return "I understood your request, but received an empty response from Gemini."

    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float,
        force_json: bool
    ) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        all_msgs = [{"role": "system", "content": system_instruction}] + messages
        payload = {
            "model": settings.AI_MODEL or "gpt-4o-mini",
            "messages": all_msgs,
            "temperature": temperature
        }
        if force_json:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_groq(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float,
        force_json: bool
    ) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        all_msgs = [{"role": "system", "content": system_instruction}] + messages
        model_name = settings.AI_MODEL if (settings.AI_MODEL and "gemini" not in settings.AI_MODEL.lower()) else "openai/gpt-oss-20b"
        payload = {
            "model": model_name,
            "messages": all_msgs,
            "temperature": temperature
        }
        if force_json:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            msg = data["choices"][0]["message"]
            return msg.get("content") or msg.get("reasoning") or "I processed your request with Groq."

    async def _call_ollama(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float,
        force_json: bool
    ) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        all_msgs = [{"role": "system", "content": system_instruction}] + messages
        payload = {
            "model": settings.AI_MODEL or "llama3",
            "messages": all_msgs,
            "stream": False,
            "options": {"temperature": temperature}
        }
        if force_json:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]

    def _local_heuristic_response(self, messages: List[Dict[str, str]], force_json: bool) -> str:
        """
        Intelligent offline heuristic engine so MAX works smoothly even without external keys.
        """
        last_message = messages[-1]["content"].lower() if messages else ""

        if force_json:
            # Check what kind of JSON response might be expected
            if "schedule" in last_message or "timetable" in last_message or "task" in last_message:
                return json.dumps({
                    "tasks": [
                        {"name": "Deep Focus Work", "duration": 60, "priority": "high", "description": "Core project focus block"},
                        {"name": "Mindful Break", "duration": 15, "priority": "low", "description": "Hydrate and stretch"},
                        {"name": "Study & Skill Review", "duration": 45, "priority": "medium", "description": "Review key learning concepts"}
                    ],
                    "notes": "Generated with MAX intelligent local scheduling engine."
                })
            return json.dumps({"status": "success", "message": "Processed offline by MAX Engine."})

        # Greetings
        if any(w in last_message for w in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            now_hour = datetime.now().hour
            greeting = "Good morning" if now_hour < 12 else "Good afternoon" if now_hour < 17 else "Good evening"
            return (
                f"{greeting}! I'm MAX, your AI executive assistant. "
                f"I'm ready to organize your timetable, track your productivity, review your goals, or teach you anything you'd like. "
                f"What are we tackling today?"
            )

        # Status / What should I do now
        if "what should i do" in last_message or "what's next" in last_message or "status" in last_message:
            return (
                "Right now, let's check your current timetable block on the dashboard! "
                "If you haven't created your schedule for today yet, just tell me what subjects or tasks you want to accomplish."
            )

        # Help / Capabilities
        if "who are you" in last_message or "what can you do" in last_message or "help" in last_message:
            return (
                "I am MAX — your personal AI executive assistant. Here is what I can do for you:\n"
                "1. **Intelligent Timetable**: Tell me what you need to study or work on, and I'll schedule realistic blocks with breaks.\n"
                "2. **Dynamic Rescheduling**: Say 'I need 30 more minutes' or 'Move coding to 5pm' and I will dynamically recalculate your day.\n"
                "3. **Voice Interaction**: Talk to me and listen to my spoken responses.\n"
                "4. **Productivity Monitoring**: With your permission, I track active focus sessions and check in when you drift.\n"
                "5. **AI Teacher**: Ask me to explain any topic from Python to Quantum Physics in simple, real-world analogies.\n"
                "6. **Long-Term Memory**: I remember your goals, habits, and preferences across sessions."
            )

        # Default conversational response
        return (
            f"Understood. I've noted that: '{messages[-1]['content']}'. "
            f"I can integrate this into your daily schedule, store it in your memory, or dive deeper into it with you. "
            f"How would you like to proceed?"
        )

ai_service = AIService()

