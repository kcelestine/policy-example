import time

import pytest

from tests.api.api_test_client import TEST_BASE_URL, \
    responses_client, HEADERS_JSON_CONTENT_TYPE, start_quiz

URI_QUIZ_SCHEDULE = f"{TEST_BASE_URL}/api/quiz-schedule"
URI_QUIZ_CHECK_STATUS = f"{TEST_BASE_URL}/api/quiz-check-status"


@pytest.mark.asyncio
async def test_quiz_schedule():
    quiz_code, user_token = await start_quiz()

    data = {"quiz_code": quiz_code, "user_token": user_token, "delay_seconds": 30}
    res = await responses_client.post(
        url=URI_QUIZ_SCHEDULE, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    assert res_json["state"]["status"] == "SCHEDULED"


@pytest.mark.asyncio
async def test_scheduled_quiz_started_automatically():
    quiz_code, user_token = await start_quiz()

    data = {"quiz_code": quiz_code, "user_token": user_token, "delay_seconds": 1}
    await responses_client.post(
        url=URI_QUIZ_SCHEDULE, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )

    # ask for the state immediately and check the state is still "SCHEDULED"
    status = await _get_quiz_state(quiz_code, user_token)
    assert status == "SCHEDULED"

    # wait 1+ seconds and the quiz should be started
    time.sleep(1.2)
    status = await _get_quiz_state(quiz_code, user_token)
    assert status == "STARTED"


async def _get_quiz_state(quiz_code: int, user_token: str) -> str:
    data = {"quiz_code": quiz_code, "user_token": user_token}
    res = await responses_client.post(
        url=URI_QUIZ_CHECK_STATUS, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    return res_json["state"]["status"]