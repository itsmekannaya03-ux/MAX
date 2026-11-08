import json
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.learning import LearningSessionModel
from backend.app.schemas.learning import LessonExplainResponse, QuizResponse, QuizQuestion
from backend.app.services.ai_service import ai_service

class LearningEngine:
    def __init__(self):
        pass

    async def explain_topic(
        self,
        topic: str,
        user_level: str = "beginner"
    ) -> LessonExplainResponse:
        """
        Generates a structured, engaging lesson breaking down the topic with:
        - Concept summary
        - Everyday real-world analogy
        - Step-by-step breakdown
        - Practical code or example
        - Comprehension check question
        """
        system_prompt = (
            "You are MAX, the world's most engaging and patient personal AI teacher. "
            "Explain the requested topic using everyday real-world analogies, crystal-clear terminology, "
            "small digestible steps, and a practical example. Return ONLY a JSON object matching this schema:\n"
            "{\n"
            '  "topic": string,\n'
            '  "level": string,\n'
            '  "concept_summary": string,\n'
            '  "everyday_analogy": string,\n'
            '  "breakdown_steps": [string, string, string],\n'
            '  "practical_code_or_example": string,\n'
            '  "comprehension_check": string\n'
            "}"
        )

        user_msg = f"Please teach me '{topic}' for a {user_level} learner."
        raw_res = await ai_service.generate_response(
            messages=[{"role": "user", "content": user_msg}],
            system_instruction=system_prompt,
            force_json=True
        )

        try:
            data = json.loads(raw_res)
            return LessonExplainResponse(
                topic=data.get("topic", topic),
                level=data.get("level", user_level),
                concept_summary=data.get("concept_summary", f"{topic} is an essential concept."),
                everyday_analogy=data.get("everyday_analogy", "Think of it like a recipe in cooking: precise steps leading to a delicious result."),
                breakdown_steps=data.get("breakdown_steps", [
                    "Step 1: Understand the fundamental purpose",
                    "Step 2: Learn the core building blocks",
                    "Step 3: Combine them into a working solution"
                ]),
                practical_code_or_example=data.get("practical_code_or_example", f"Example in practice: using {topic} to automate a daily task."),
                comprehension_check=data.get("comprehension_check", "In your own words, what main problem does this solve?")
            )
        except Exception:
            # Fallback pedagogical template
            return LessonExplainResponse(
                topic=topic,
                level=user_level,
                concept_summary=f"{topic} is a key topic that allows you to build solutions, solve problems, and structure logic cleanly.",
                everyday_analogy=f"Imagine {topic} like a well-organized toolbox: every single tool has a designated compartment so you can build anything efficiently without chaos.",
                breakdown_steps=[
                    f"1. Core Purpose: Why {topic} exists and what fundamental bottleneck it eliminates.",
                    f"2. Practical Mechanism: How the input is taken, processed step-by-step, and converted to output.",
                    f"3. Real Application: How modern engineers, scientists, and students use {topic} daily."
                ],
                practical_code_or_example=f"# Practical illustration for {topic}\ndef practical_demo():\n    print('Understanding {topic} is step 1 to mastery!')\n\npractical_demo()",
                comprehension_check=f"What is one everyday situation where you think the principles of {topic} could be applied?"
            )

    async def generate_quiz(
        self,
        db: Session,
        topic: str,
        num_questions: int = 3,
        level: str = "beginner"
    ) -> QuizResponse:
        system_prompt = (
            "You are MAX's quiz generation engine. Generate high quality multiple-choice questions "
            "to test a student's understanding. Return ONLY a JSON object with this schema:\n"
            "{\n"
            '  "questions": [\n'
            '    {\n'
            '      "id": 1,\n'
            '      "question": "string",\n'
            '      "options": ["Option A", "Option B", "Option C", "Option D"],\n'
            '      "correct_option_index": 0,\n'
            '      "explanation": "string"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        user_msg = f"Generate {num_questions} quiz questions on '{topic}' for level '{level}'."
        raw_res = await ai_service.generate_response(
            messages=[{"role": "user", "content": user_msg}],
            system_instruction=system_prompt,
            force_json=True
        )

        questions: List[QuizQuestion] = []
        try:
            data = json.loads(raw_res)
            for idx, q in enumerate(data.get("questions", [])):
                questions.append(QuizQuestion(
                    id=idx + 1,
                    question=q["question"],
                    options=q["options"],
                    correct_option_index=int(q["correct_option_index"]),
                    explanation=q["explanation"]
                ))
        except Exception:
            pass

        if not questions:
            questions = [
                QuizQuestion(
                    id=1,
                    question=f"What is the primary purpose of {topic}?",
                    options=[
                        "To structure and solve specific problems reliably",
                        "To replace all human thinking completely",
                        "To delete old files without permission",
                        "To slow down processing times"
                    ],
                    correct_option_index=0,
                    explanation=f"{topic} is designed to provide structured problem-solving capabilities."
                ),
                QuizQuestion(
                    id=2,
                    question=f"Which practice is most effective when working with {topic}?",
                    options=[
                        "Skipping fundamentals and guessing randomly",
                        "Breaking problems into small, verifiable chunks",
                        "Ignoring syntax and documentation",
                        "Never testing edge cases"
                    ],
                    correct_option_index=1,
                    explanation="Modular decomposition and testing small parts guarantees high reliability."
                )
            ]

        session_entry = LearningSessionModel(
            topic=topic,
            level=level,
            summary=f"Interactive Quiz on {topic}",
            quiz_data=json.dumps([q.model_dump() for q in questions])
        )
        db.add(session_entry)
        db.commit()
        db.refresh(session_entry)

        return QuizResponse(
            session_id=session_entry.id,
            topic=topic,
            questions=questions
        )

    def submit_quiz(
        self,
        db: Session,
        session_id: int,
        user_answers: List[int]
    ) -> Dict[str, Any]:
        stmt = select(LearningSessionModel).where(LearningSessionModel.id == session_id)
        session_entry = db.scalars(stmt).first()

        if not session_entry:
            return {"error": "Quiz session not found."}

        quiz_questions = json.loads(session_entry.quiz_data)
        correct_count = 0
        details = []

        for idx, q in enumerate(quiz_questions):
            user_ans = user_answers[idx] if idx < len(user_answers) else -1
            is_correct = (user_ans == q["correct_option_index"])
            if is_correct:
                correct_count += 1
            details.append({
                "question": q["question"],
                "your_answer": q["options"][user_ans] if 0 <= user_ans < len(q["options"]) else "Unanswered",
                "correct_answer": q["options"][q["correct_option_index"]],
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })

        session_entry.quiz_score = correct_count
        session_entry.quiz_total = len(quiz_questions)
        db.commit()

        percentage = int((correct_count / len(quiz_questions)) * 100) if quiz_questions else 0
        feedback = (
            f"Spectacular! You scored {correct_count}/{len(quiz_questions)} ({percentage}%). Perfect comprehension!"
            if percentage >= 80 else
            f"Good effort! You scored {correct_count}/{len(quiz_questions)} ({percentage}%). Let's review the missed concepts."
        )

        return {
            "session_id": session_id,
            "score": correct_count,
            "total": len(quiz_questions),
            "percentage": percentage,
            "feedback": feedback,
            "detailed_answers": details
        }

learning_engine = LearningEngine()
