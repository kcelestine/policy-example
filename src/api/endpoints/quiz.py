from typing import List, Dict, Any

from fastapi import APIRouter

from domain.quiz_manager import quiz_manager
from domain.quiz_requests import QuizStartRequest

router = APIRouter()


@router.get("/quiz-topics")
async def get_topics() -> List[Dict[str, Any]]:
    return [q.to_dict() for q in quiz_manager.get_quiz_topics()]


@router.post("/quiz-start")
async def start_quiz(request_data: QuizStartRequest) -> Dict[str, Any]:
    return quiz_manager.start_quiz(request_data).to_dict()
