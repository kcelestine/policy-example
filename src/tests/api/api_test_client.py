from httpx import AsyncClient

from main import app

TEST_BASE_URL = "http://test"
HEADERS_JSON_CONTENT_TYPE = {"Content-Type": "application/json"}

responses_client = AsyncClient(app=app, base_url=TEST_BASE_URL)
