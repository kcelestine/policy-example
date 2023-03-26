from typing import List, Dict, Any

import pytest
from freezegun import freeze_time

from tests.api.api_test_client import TEST_BASE_URL, responses_client, HEADERS_JSON_CONTENT_TYPE, start_quiz

URI_QUIZ_GIVE_ANSWER = f"{TEST_BASE_URL}/api/quiz-answer"
URI_QUIZ_SCHEDULE = f"{TEST_BASE_URL}/api/quiz-schedule"
URI_QUIZ_JOIN = f"{TEST_BASE_URL}/api/quiz-join"
URI_QUIZ_RESULTS = f"{TEST_BASE_URL}/api/quiz-results"


@pytest.mark.asyncio
@freeze_time("2012-01-14 10:00:00.000")
async def test_finish_quiz_and_get_results():
    quiz_code, commander_token = await start_quiz(question_seconds=1)

    # let the second player join
    data = {"quiz_code": quiz_code, "user_name": "Bart"}
    res = await responses_client.post(
        url=URI_QUIZ_JOIN, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    second_usr_token = res_json["user"]["user_token"]

    # schedule the quiz
    await _schedule_quiz(quiz_code, commander_token)

    # wait 1+ seconds to start the quiz and let the commander-player answer
    with freeze_time("2012-01-14 10:00:01.550"):
        await _give_answer(commander_token, quiz_code, 0, [1])
    # wait a bit more and let the second player answer
    with freeze_time("2012-01-14 10:00:01.750"):
        await _give_answer(second_usr_token, quiz_code, 0, [1])
    # wait until the second question is available and let the 2nd player answer
    with freeze_time("2012-01-14 10:00:02.450"):
        await _give_answer(second_usr_token, quiz_code, 1, [0, 2])
    # wait until the quiz ends and then let the 1st player give his answer
    with freeze_time("2012-01-14 10:00:06"):
        with pytest.raises(Exception):
            # the exception is raised because the answer came too late
            await _give_answer(commander_token, quiz_code, 1, [0, 2])
    # now let's check the quiz results
    results = await _get_quiz_results(quiz_code)
    assert results


async def _give_answer(token: str, quiz_code: int,
                       question_index: int, answer: List[int]) -> None:
    data = {"quiz_code": quiz_code, "user_token": token,
            "question_index": question_index, "answer": answer}
    await responses_client.post(
        url=URI_QUIZ_GIVE_ANSWER, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )


async def _schedule_quiz(quiz_code: int, token: str) -> None:
    data = {"quiz_code": quiz_code, "user_token": token, "delay_seconds": 1}
    await responses_client.post(
        url=URI_QUIZ_SCHEDULE, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )


async def _get_quiz_results(quiz_code: int) -> Dict[str, Any]:
    url = f"{URI_QUIZ_RESULTS}/{quiz_code}"
    results = await responses_client.get(
        url=url
    )
    return results.json()
