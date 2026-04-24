# tests/test_api.py

from fastapi.testclient import TestClient  # type: ignore[import]

import api.main as main

client = TestClient(main.app)


def test_get_patient_success(monkeypatch) -> None:
    def fake_get_patient_by_id(patient_id: int):
        return {
            "patient_id": patient_id,
            "first_name": "Alice",
            "last_name": "Johnson",
            "date_of_birth": "1980-03-15",
            "sex": "F",
            "age": 46,
        }

    monkeypatch.setattr(main, "get_patient_by_id", fake_get_patient_by_id)

    response = client.get("/patients/1")

    assert response.status_code == 200
    assert response.json()["patient_id"] == 1
    assert response.json()["age"] == 46


def test_get_patient_not_found(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_patient_by_id", lambda patient_id: None)

    response = client.get("/patients/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient 999 not found."


def test_get_patient_labs_success(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "get_patient_by_id",
        lambda patient_id: {"patient_id": patient_id, "age": 46},
    )

    monkeypatch.setattr(
        main,
        "get_patient_labs",
        lambda patient_id: [
            {
                "lab_id": 1,
                "patient_id": patient_id,
                "lab_name": "glucose",
                "value": 95.0,
                "unit": "mg/dL",
                "collected_at": "2026-01-10 08:30:00",
                "abnormal": False,
            }
        ],
    )

    response = client.get("/patients/1/labs")

    assert response.status_code == 200
    assert response.json()[0]["lab_name"] == "glucose"
    assert response.json()[0]["abnormal"] is False


def test_get_patient_labs_patient_not_found(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_patient_by_id", lambda patient_id: None)

    response = client.get("/patients/999/labs")

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient 999 not found."


def test_get_abnormal_labs_all_patients(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "get_abnormal_labs",
        lambda patient_id=None: [
            {
                "lab_id": 4,
                "patient_id": 2,
                "lab_name": "glucose",
                "value": 210.0,
                "unit": "mg/dL",
                "collected_at": "2026-02-14 09:00:00",
                "abnormal": True,
            }
        ],
    )

    response = client.get("/labs/abnormal")

    assert response.status_code == 200
    assert response.json()[0]["patient_id"] == 2
    assert response.json()[0]["abnormal"] is True


def test_get_abnormal_labs_filtered_by_patient(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "get_patient_by_id",
        lambda patient_id: {"patient_id": patient_id, "age": 80},
    )

    monkeypatch.setattr(
        main,
        "get_abnormal_labs",
        lambda patient_id=None: [
            {
                "lab_id": 4,
                "patient_id": patient_id,
                "lab_name": "glucose",
                "value": 210.0,
                "unit": "mg/dL",
                "collected_at": "2026-02-14 09:00:00",
                "abnormal": True,
            }
        ],
    )

    response = client.get("/labs/abnormal?patient_id=2")

    assert response.status_code == 200
    assert response.json()[0]["patient_id"] == 2


def test_get_abnormal_labs_patient_not_found(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_patient_by_id", lambda patient_id: None)

    response = client.get("/labs/abnormal?patient_id=999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient 999 not found."
