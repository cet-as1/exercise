"""Pytest configuration and shared fixtures for testing the Mergington High School API."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def clean_app():
    """
    Fixture: Provide a fresh FastAPI app instance with clean in-memory activities.
    
    This ensures test isolation by resetting the activities dictionary to a known state
    before each test.
    """
    # Reset activities to a known clean state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    return app


@pytest.fixture
def client(clean_app):
    """
    Fixture: Provide a FastAPI TestClient for making test requests.
    
    Depends on clean_app fixture to ensure fresh state before each test.
    """
    return TestClient(clean_app)


@pytest.fixture
def sample_email():
    """Fixture: Provide a sample email for testing signup/removal."""
    return "newstudent@mergington.edu"


@pytest.fixture
def existing_participant():
    """Fixture: Provide an email already enrolled in an activity."""
    return "michael@mergington.edu"
