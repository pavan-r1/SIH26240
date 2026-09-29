from fastapi.testclient import TestClient

from backend.database import get_db
from backend.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cors_allows_localhost_frontend():
    response = client.get("/api/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_preflight_allows_dashboard_request():
    response = client.options(
        "/api/dashboard",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "GET" in response.headers["access-control-allow-methods"]


def test_weather_is_explicitly_unconfigured():
    response = client.get("/api/weather")
    assert response.status_code == 200
    assert response.json()["status"] == "NOT CONFIGURED"


def test_recharge_readiness_does_not_claim_inputs():
    class EmptyResult:
        def all(self): return []
    class EmptyDatabase:
        def scalars(self, _statement): return EmptyResult()
    app.dependency_overrides[get_db] = lambda: EmptyDatabase()
    try:
        response = client.get("/api/recharge/readiness")
        assert response.status_code == 200
        assert response.json()["can_analyze"] is False
        assert "DEM" in response.json()["missing_parameters"]
    finally:
        app.dependency_overrides.clear()


def test_recharge_analysis_does_not_create_prediction_without_data():
    response = client.post("/api/recharge/analyze")
    assert response.status_code == 409
    assert response.json()["detail"]["prediction_created"] is False
