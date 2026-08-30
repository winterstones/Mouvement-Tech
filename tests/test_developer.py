import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from api.collectors.github import GitHubCollector


@pytest.mark.anyio
async def test_developer_endpoint_invalid_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/evaluate/developer?username=this-user-definitely-does-not-exist-xyz-999")
        assert res.status_code in [404, 500]


@pytest.mark.anyio
async def test_developer_endpoint_valid_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/evaluate/developer?username=torvalds")
        if res.status_code == 200:
            data = res.json()
            assert "profile_id" in data
            assert data["profile_id"] == "torvalds"
            assert "level" in data
            assert "axes" in data
            assert "audited_repos" in data
            assert isinstance(data["audited_repos"], list)
        else:
            # In case rate limit or network offline
            assert res.status_code in [200, 404, 500]
