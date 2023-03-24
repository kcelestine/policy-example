import pytest

from tests.api.api_test_client import TEST_BASE_URL, responses_client, HEADERS_JSON_CONTENT_TYPE

URI_QUIZ_START = f"{TEST_BASE_URL}/api/quiz-start"


@pytest.mark.asyncio
async def test_quiz_start():
    data = {"topic_id": "d729af45-5ed3-42d0-ac57-d4485b64b067", "user_name": "Alph"}
    res = await responses_client.post(
        url=URI_QUIZ_START, headers=HEADERS_JSON_CONTENT_TYPE, json=data
    )
    res_json = res.json()
    assert "user" in res_json
    assert "state" in res_json
    assert "all_user_names" in res_json
    assert len(res_json["all_user_names"]) == 1
