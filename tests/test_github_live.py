import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from api.collectors.github import GitHubCollector


def test_parse_repo_url():
    owner, repo = GitHubCollector.parse_repo_url("https://github.com/ai-driven-dev/laivel-up")
    assert owner == "ai-driven-dev"
    assert repo == "laivel-up"

    owner2, repo2 = GitHubCollector.parse_repo_url("git@github.com:fastapi/fastapi.git")
    assert owner2 == "fastapi"
    assert repo2 == "fastapi"


@pytest.mark.anyio
async def test_evaluate_live_repo_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test evaluating public repo laivel-up
        res = await client.get("/evaluate/live?repo_url=https://github.com/ai-driven-dev/laivel-up")
        if res.status_code == 200:
            data = res.json()
            assert "level" in data
            assert "axes" in data
            assert data["profile_id"] == "ai-driven-dev/laivel-up"
        else:
            # In case of GitHub API rate limit (HTTP 400 with message), it gracefully returns clear error
            assert res.status_code in [200, 400]
