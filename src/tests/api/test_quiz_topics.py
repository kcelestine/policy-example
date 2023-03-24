import pytest

from tests.api.api_test_client import TEST_BASE_URL, responses_client

URI_QUIZ_TOPICS = f"{TEST_BASE_URL}/api/quiz-topics"


# this lines requires the package "pytest-asyncio"
@pytest.mark.asyncio
async def test_get_topics():
    # data = {"assignment_id": assignment_id}
    res = await responses_client.get(
        url=URI_QUIZ_TOPICS, headers={} #, json=data
    )
    res_json = res.json()
    assert len(res_json) == 2
