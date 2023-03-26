import pytest
from freezegun import freeze_time

from tests.api.api_test_client import TEST_BASE_URL, responses_client, HEADERS_JSON_CONTENT_TYPE, start_quiz

URI_QUIZ_GIVE_ANSWER = f"{TEST_BASE_URL}/api/quiz-answer"
URI_QUIZ_SCHEDULE = f"{TEST_BASE_URL}/api/quiz-schedule"


@pytest.mark.asyncio
@freeze_time("2012-01-14 10:00:00.000")
async def test_give_second_answer():
    quiz_code, token = await start_quiz(question_seconds=1)
    # schedule the quiz
    data = {"quiz_code": quiz_code, "user_token": token, "delay_seconds": 1}
    await responses_client.post(
        url=URI_QUIZ_SCHEDULE, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )

    # wait 2+ seconds to check the current question is set to the question #2
    data = {"quiz_code": quiz_code, "user_token": token, "question_index": 1, "answer": [0, 2]}
    with freeze_time("2012-01-14 10:00:02.550"):
        res = await responses_client.post(
            url=URI_QUIZ_GIVE_ANSWER, headers=HEADERS_JSON_CONTENT_TYPE, json=data
        )
    res_json = res.json()
    assert res_json
    # NB: tuple (0, 2) is deserialized as an array [0, 2]
    assert res_json["state"]["cur_question_index"] == [1, 2]
    # NB: the /api/quiz-answer request actually caused the quiz's state update
    # from SCHEDULED to STARTED
    assert res_json["state"]["status"] == "STARTED"
    assert res_json["user"]["answers"][0]["answer"] == []
    assert res_json["user"]["answers"][1]["answer"] == [0, 2]

    # now we can't give answer to the previous question
    data = {"quiz_code": quiz_code, "user_token": token, "question_index": 0, "answer": [0, 2]}
    with freeze_time("2012-01-14 10:00:02.550"):
        result = await responses_client.post(
            url=URI_QUIZ_GIVE_ANSWER, headers=HEADERS_JSON_CONTENT_TYPE, json=data
        )
        assert result.status_code == 500
