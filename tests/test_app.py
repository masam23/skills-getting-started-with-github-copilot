"""
Tests for the FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for getting activities"""

    def test_get_activities_returns_200(self):
        """Test that /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities response contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Drama Club" in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignup:
    """Tests for signing up for activities"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self):
        """Test that signup adds participant to activity"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])

        # Sign up
        client.post("/activities/Chess%20Club/signup?email=newuser@mergington.edu")

        # Check count increased
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 1

    def test_signup_duplicate_email_fails(self):
        """Test that signing up with same email twice fails"""
        email = "duplicate@mergington.edu"
        # First signup
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response1.status_code == 200

        # Second signup with same email
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signup to nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregister:
    """Tests for unregistering from activities"""

    def test_unregister_success(self):
        """Test successful unregister from activity"""
        # First sign up
        email = "unregister_test@mergington.edu"
        client.post(f"/activities/Drama%20Club/signup?email={email}")

        # Then unregister
        response = client.post(f"/activities/Drama%20Club/unregister?email={email}")
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from activity"""
        email = "remove_test@mergington.edu"
        # Sign up
        client.post(f"/activities/Art%20Studio/signup?email={email}")

        # Get count before unregister
        response = client.get("/activities")
        count_before = len(response.json()["Art Studio"]["participants"])

        # Unregister
        client.post(f"/activities/Art%20Studio/unregister?email={email}")

        # Check count decreased
        response = client.get("/activities")
        count_after = len(response.json()["Art Studio"]["participants"])
        assert count_after == count_before - 1

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregister from nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_not_registered_fails(self):
        """Test that unregistering someone not registered fails"""
        email = "not_registered@mergington.edu"
        response = client.post(f"/activities/Chess%20Club/unregister?email={email}")
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]


class TestRoot:
    """Tests for root endpoint"""

    def test_root_redirects(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
