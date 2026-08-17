"""Integration tests for Mergington High School API endpoints using AAA pattern."""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """
        Test: GET /activities returns 200 with all activities.
        
        Arrange: Setup via fixture (client)
        Act: GET /activities
        Assert: Status 200 + activities list returned
        """
        # Arrange
        # (client fixture provides TestClient with clean app state)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activities_response_structure(self, client):
        """
        Test: Activities response includes required fields.
        
        Arrange: Setup via fixture
        Act: GET /activities and inspect structure
        Assert: Each activity has description, schedule, max_participants, participants
        """
        # Arrange
        # (client fixture provides TestClient with clean app state)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_participant_count_is_accurate(self, client):
        """
        Test: Participant count matches length of participants list.
        
        Arrange: Fetch activities
        Act: Verify participant count logic
        Assert: Count = len(participants) for each activity
        """
        # Arrange
        # (client fixture provides TestClient with clean app state)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_happy_path(self, client, sample_email):
        """
        Test: Successful signup adds email to activity participants.
        
        Arrange: Valid email and activity name
        Act: POST /activities/Chess Club/signup?email=newstudent@mergington.edu
        Assert: Status 200 + success message + email in participants
        """
        # Arrange
        email = sample_email
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify email was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client, sample_email):
        """
        Test: Signup to nonexistent activity returns 404.
        
        Arrange: Invalid activity name
        Act: POST /activities/Nonexistent Club/signup
        Assert: Status 404 + error message
        """
        # Arrange
        email = sample_email
        activity_name = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email(self, client, existing_participant):
        """
        Test: Signup with already-enrolled email returns 400.
        
        Arrange: Email already in Chess Club (michael@mergington.edu)
        Act: POST same email to same activity
        Assert: Status 400 + duplicate error message
        """
        # Arrange
        email = existing_participant  # Already in Chess Club
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_multiple_activities_same_email(self, client, sample_email):
        """
        Test: Same email can sign up for multiple different activities.
        
        Arrange: Sample email (not yet enrolled anywhere)
        Act: Signup to Chess Club, then Programming Class
        Assert: Both signups succeed (200), email in both activities
        """
        # Arrange
        email = sample_email
        
        # Act
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestRemove:
    """Test suite for DELETE /activities/{activity_name}/remove endpoint."""

    def test_remove_happy_path(self, client, existing_participant):
        """
        Test: Successful removal removes email from activity participants.
        
        Arrange: Email already enrolled (michael@mergington.edu in Chess Club)
        Act: DELETE /activities/Chess Club/remove?email=michael@mergington.edu
        Assert: Status 200 + success message + email removed from participants
        """
        # Arrange
        email = existing_participant
        activity_name = "Chess Club"
        
        # Verify email is initially in the activity
        activities_before = client.get("/activities").json()
        assert email in activities_before[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify email was actually removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after[activity_name]["participants"]

    def test_remove_activity_not_found(self, client, existing_participant):
        """
        Test: Remove from nonexistent activity returns 404.
        
        Arrange: Invalid activity name
        Act: DELETE /activities/Nonexistent Club/remove
        Assert: Status 404 + error message
        """
        # Arrange
        email = existing_participant
        activity_name = "Nonexistent Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_student_not_enrolled(self, client, sample_email):
        """
        Test: Remove non-enrolled student returns 400.
        
        Arrange: Email not enrolled in activity
        Act: DELETE /activities/Chess Club/remove with non-enrolled email
        Assert: Status 400 + error message
        """
        # Arrange
        email = sample_email  # Not enrolled anywhere
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()


class TestRoot:
    """Test suite for GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """
        Test: GET / redirects to /static/index.html.
        
        Arrange: Setup via fixture
        Act: GET /
        Assert: Status 307/302 + Location header points to /static/index.html
        """
        # Arrange
        # (client fixture provides TestClient with clean app state)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code in [307, 302]
        assert "/static/index.html" in response.headers.get("location", "")
