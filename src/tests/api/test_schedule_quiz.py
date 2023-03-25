import pytest

from tests.api.api_test_client import TEST_BASE_URL, \
    responses_client, HEADERS_JSON_CONTENT_TYPE, start_quiz

URI_QUIZ_SCHEDULE = f"{TEST_BASE_URL}/api/quiz-schedule"


@pytest.mark.asyncio
async def test_quiz_schedule():
    quiz_code, user_token = await start_quiz()

    data = {"quiz_code": quiz_code, "user_token": user_token, "delay_seconds": 30}
    res = await responses_client.post(
        url=URI_QUIZ_SCHEDULE, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    assert res_json["state"]["status"] == "SCHEDULED"
