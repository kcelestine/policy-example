import pytest

from tests.api.api_test_client import TEST_BASE_URL, responses_client, HEADERS_JSON_CONTENT_TYPE, start_quiz

URI_QUIZ_JOIN = f"{TEST_BASE_URL}/api/quiz-join"


@pytest.mark.asyncio
async def test_quiz_join():
    quiz_code, _ = await start_quiz()

    data = {"quiz_code": quiz_code, "user_name": "Bart"}
    res = await responses_client.post(
        url=URI_QUIZ_JOIN, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    assert "user" in res_json
    assert "state" in res_json
    assert "all_user_names" in res_json
    assert len(res_json["all_user_names"]) == 2
    assert "Bart" in res_json["all_user_names"]
