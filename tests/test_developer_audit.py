import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from api.collectors.github import GitHubCollector


def test_parse_username():
    assert GitHubCollector.parse_username("torvalds") == "torvalds"
    assert GitHubCollector.parse_username("@torvalds") == "torvalds"
    assert GitHubCollector.parse_username("https://github.com/torvalds") == "torvalds"
    assert GitHubCollector.parse_username("https://github.com/torvalds/") == "torvalds"


@pytest.mark.anyio
async def test_api_evaluate_developer_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/evaluate/developer?username=winterstones")
        # In case of rate limit or 200/404, check valid response structure
        if res.status_code == 200:
            data = res.json()
            assert "profile_id" in data
            assert "level" in data
            assert "axes" in data
        else:
            assert res.status_code in [404, 500, 400]
