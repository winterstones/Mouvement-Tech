import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.anyio
async def test_api_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert res.json()["app"] == "Mouvement-Tech"


@pytest.mark.anyio
async def test_api_levels():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/levels")
        assert res.status_code == 200
        data = res.json()
        assert len(data["levels"]) == 7


@pytest.mark.anyio
async def test_api_evaluate_bohort():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/evaluate/bohort")
        assert res.status_code == 200
        data = res.json()
        assert data["level"]["id"] == "blue"
        assert data["profile_id"] == "bohort"
        assert "progression" in data
