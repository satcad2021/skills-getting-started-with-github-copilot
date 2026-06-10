import copy

import pytest
from fastapi.testclient import TestClient

from src import app as application_module

client = TestClient(application_module.app)
initial_activities = copy.deepcopy(application_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    application_module.activities.clear()
    application_module.activities.update(copy.deepcopy(initial_activities))
    yield


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert payload["Chess Club"]["participants"] == []


def test_signup_for_activity_adds_participant():
    email = "student@example.com"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in application_module.activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_bad_request():
    email = "student@example.com"
    client.post("/activities/Chess%20Club/signup", params={"email": email})

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_participant():
    email = "student@example.com"
    client.post("/activities/Chess%20Club/signup", params={"email": email})

    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in application_module.activities["Chess Club"]["participants"]


def test_unregister_missing_activity_returns_not_found():
    response = client.delete(
        "/activities/Nonexistent%20Club/participants",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_nonexistent_participant_returns_not_found():
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "absent@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
