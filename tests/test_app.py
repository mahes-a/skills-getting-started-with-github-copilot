import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Save the original activities for test isolation
@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    # Restore original state after each test
    activities.clear()
    activities.update(copy.deepcopy(original))

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_and_unregister():
    test_email = "pytestuser@mergington.edu"
    activity = "Chess Club"

    # Ensure not already signed up (ignore error if not present)
    client.post(f"/activities/{activity}/unregister", params={"email": test_email})

    # Sign up
    response = client.post(f"/activities/{activity}/signup", params={"email": test_email})
    assert response.status_code == 200
    assert f"Signed up {test_email}" in response.json()["message"]

    # Check participant is added
    activities_resp = client.get("/activities").json()
    assert test_email in activities_resp[activity]["participants"]

    # Unregister
    response = client.post(f"/activities/{activity}/unregister", params={"email": test_email})
    assert response.status_code == 200
    assert f"Removed {test_email}" in response.json()["message"]

    # Check participant is removed
    activities_resp = client.get("/activities").json()
    assert test_email not in activities_resp[activity]["participants"]
