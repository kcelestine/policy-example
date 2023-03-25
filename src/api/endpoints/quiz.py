from typing import List, Dict, Any

from fastapi import APIRouter

from domain.quiz_manager import quiz_manager
from domain.quiz_requests import QuizStartRequest, QuizJoinRequest, QuizStatusRequest, ScheduleQuizRequest

router = APIRouter()


@router.get("/quiz-topics")
async def get_topics() -> List[Dict[str, Any]]:
    return [q.to_dict() for q in quiz_manager.get_quiz_topics()]


@router.post("/quiz-start")
async def start_quiz(request_data: QuizStartRequest) -> Dict[str, Any]:
    return quiz_manager.start_quiz(request_data).to_dict()


@router.post("/quiz-join")
async def join_quiz(request_data: QuizJoinRequest) -> Dict[str, Any]:
    return quiz_manager.join_quiz(request_data).to_dict()


@router.post("/quiz-check-status")
async def check_status(request_data: QuizStatusRequest) -> Dict[str, Any]:
    return quiz_manager.get_quiz_status(request_data).to_dict()


@router.post("/quiz-schedule")
async def schedule_quiz(request_data: ScheduleQuizRequest) -> Dict[str, Any]:
    return quiz_manager.schedule_quiz(request_data).to_dict()
