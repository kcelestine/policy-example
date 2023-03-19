import uuid

from fastapi import APIRouter

router = APIRouter()


@router.get("/quiz-topics")
@router.get("/quiz-topics/")
async def get_topics() -> dict:
    hardcoded_topics = {
        "topics": [
            {"id": str(uuid.uuid4()), "name": "Animals"},
            {"id": str(uuid.uuid4()), "name": "Planet"}
        ]
    }
    return hardcoded_topics
