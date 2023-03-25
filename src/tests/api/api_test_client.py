from typing import Tuple

from httpx import AsyncClient

from main import app

TEST_BASE_URL = "http://test"
URI_QUIZ_START = f"{TEST_BASE_URL}/api/quiz-start"
HEADERS_JSON_CONTENT_TYPE = {"Content-Type": "application/json"}

responses_client = AsyncClient(app=app, base_url=TEST_BASE_URL)


async def start_quiz() -> Tuple[int, str]:
    data = {"topic_id": "d729af45-5ed3-42d0-ac57-d4485b64b067", "user_name": "Alph"}
    res = await responses_client.post(
        url=URI_QUIZ_START, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    return res_json["state"]["quiz_code"], res_json["user"]["user_token"]
