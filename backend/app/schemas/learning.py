from pydantic import BaseModel
from typing import List, Optional

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str

class LessonExplainRequest(BaseModel):
    topic: str
    user_level: str = "beginner" # beginner, intermediate, advanced
    style: str = "analogies_and_steps"

class LessonExplainResponse(BaseModel):
    topic: str
    level: str
    concept_summary: str
    breakdown_steps: List[str]
    everyday_analogy: str
    practical_code_or_example: str
    comprehension_check: str

class QuizGenerateRequest(BaseModel):
    topic: str
    num_questions: int = 3
    level: str = "beginner"

class QuizResponse(BaseModel):
    session_id: int
    topic: str
    questions: List[QuizQuestion]

class QuizSubmitRequest(BaseModel):
    session_id: int
    answers: List[int] # user selected indices

class QuizResultResponse(BaseModel):
    session_id: int
    score: int
    total: int
    feedback: str
    detailed_answers: List[dict]

