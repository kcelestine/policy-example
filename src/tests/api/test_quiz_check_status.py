import time

import pytest

from tests.api.api_test_client import TEST_BASE_URL, responses_client, HEADERS_JSON_CONTENT_TYPE, start_quiz

URI_QUIZ_CHECK_STATUS = f"{TEST_BASE_URL}/api/quiz-check-status"
URI_QUIZ_SCHEDULE = f"{TEST_BASE_URL}/api/quiz-schedule"


@pytest.mark.asyncio
async def test_quiz_check_status():
    quiz_code, token = await start_quiz()

    data = {"quiz_code": quiz_code, "user_token": token}
    res = await responses_client.post(
        url=URI_QUIZ_CHECK_STATUS, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    assert "user" in res_json
    assert "state" in res_json
    assert "all_user_names" in res_json
    assert len(res_json["all_user_names"]) == 1
    assert "Alph" in res_json["all_user_names"]


@pytest.mark.asyncio
async def test_quiz_current_question_is_set():
    quiz_code, token = await start_quiz(question_seconds=1)
    # schedule the quiz
    data = {"quiz_code": quiz_code, "user_token": token, "delay_seconds": 1}
    await responses_client.post(
        url=URI_QUIZ_SCHEDULE, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )

    # wait 1+ seconds to check the current question is set to the question #1
    time.sleep(1.2)
    data = {"quiz_code": quiz_code, "user_token": token}
    res = await responses_client.post(
        url=URI_QUIZ_CHECK_STATUS, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    assert res_json
    # NB: tuple (0, 2) is deserialized as an array [0, 2]
    assert res_json["state"]["cur_question_index"] == [0, 2]
    assert res_json["state"]["cur_question"]["question_type"] == "SINGLE_CHOICE"

    # wait 1+ seconds to check the current question is set to the question #2
    time.sleep(1)
    data = {"quiz_code": quiz_code, "user_token": token}
    res = await responses_client.post(
        url=URI_QUIZ_CHECK_STATUS, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    assert res_json
    assert res_json["state"]["cur_question_index"] == [1, 2]
    assert res_json["state"]["cur_question"]["question_type"] == "MULTI_CHOICE"
