from fastapi.testclient import TestClient

from app.main import app


def test_healthz() -> None:
    c = TestClient(app)
    res = c.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_health_alias() -> None:
    c = TestClient(app)
    res = c.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
