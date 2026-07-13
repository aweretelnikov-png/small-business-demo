from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_lead_returns_422() -> None:
    response = client.post(
        "/api/leads",
        json={
            "name": "Иван",
            "phone": "abcdefghij",
            "service": "hidden-door",
            "district": "Москва",
            "desired_date": None,
            "comment": None,
            "consent": True,
        },
    )

    assert response.status_code == 422


def test_valid_lead_returns_real_service_id(monkeypatch) -> None:
    saved_lead = {}

    def fake_save_lead(lead) -> int:
        saved_lead["phone"] = lead.phone
        return 42

    monkeypatch.setattr("app.main.save_lead", fake_save_lead)

    response = client.post(
        "/api/leads",
        json={
            "name": "Иван",
            "phone": "8 (999) 111-22-33",
            "service": "hidden-door",
            "district": "Москва",
            "desired_date": None,
            "comment": "Тест",
            "consent": True,
        },
    )

    assert response.status_code == 201
    assert response.json() == {"lead_id": 42, "status": "created"}
    assert saved_lead["phone"] == "+79991112233"
