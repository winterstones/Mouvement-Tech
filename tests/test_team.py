import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from tests.test_profiles import evaluate_profile_by_id
from api.scorer.team import TeamEngine


def test_team_engine_evaluation():
    perceval = evaluate_profile_by_id("perceval")
    bohort = evaluate_profile_by_id("bohort")
    leodagan = evaluate_profile_by_id("leodagan")
    arthur = evaluate_profile_by_id("arthur")

    team_res = TeamEngine.evaluate_team([perceval, bohort, leodagan, arthur], team_name="Team Kaamelott")

    assert team_res.team_size == 4
    # (1 + 2 + 3 + 4) / 4 = 2.5
    assert team_res.average_rank == 2.5
    assert team_res.level_distribution["red"] == 1
    assert team_res.level_distribution["blue"] == 1
    assert team_res.level_distribution["green"] == 1
    assert team_res.level_distribution["copper"] == 1
    assert len(team_res.team_recommendations) >= 3


@pytest.mark.anyio
async def test_team_api_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/team")
        assert res.status_code == 200
        data = res.json()
        assert data["team_size"] == 4
        assert data["average_rank"] == 2.5
        assert len(data["members"]) == 4
        assert "team_recommendations" in data


@pytest.mark.anyio
async def test_team_contributors_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/team/contributors?repo_url=https://github.com/ai-driven-dev/laivel-up")
        if res.status_code == 200:
            data = res.json()
            assert isinstance(data, list)
        else:
            assert res.status_code in [200, 400]
