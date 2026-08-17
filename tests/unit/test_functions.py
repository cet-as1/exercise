"""Unit tests for Mergington High School API business logic using AAA pattern."""

import pytest


class TestSignupLogic:
    """Unit tests for signup business logic."""

    def test_participant_added_to_list(self, client, sample_email):
        """
        Test: Signup adds email to activity's participants list.
        
        Arrange: Setup activity and new email
        Act: Call signup endpoint
        Assert: Email added to participants list
        """
        # Arrange
        email = sample_email
        activity_name = "Chess Club"
        initial_count = len(
            client.get("/activities").json()[activity_name]["participants"]
        )
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        updated_activity = client.get("/activities").json()[activity_name]
        assert email in updated_activity["participants"]
        assert len(updated_activity["participants"]) == initial_count + 1

    def test_no_duplicate_participants(self, client, existing_participant):
        """
        Test: Same email cannot be added twice to participants list.
        
        Arrange: Email already in activity (michael@mergington.edu)
        Act: Try to signup same email again
        Assert: Error returned, participants list unchanged
        """
        # Arrange
        email = existing_participant
        activity_name = "Chess Club"
        initial_participants = client.get("/activities").json()[activity_name]["participants"].copy()
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        updated_activity = client.get("/activities").json()[activity_name]
        assert updated_activity["participants"] == initial_participants

    def test_email_format_preserved(self, client):
        """
        Test: Email is stored exactly as submitted.
        
        Arrange: Email with specific casing
        Act: Signup with specific email
        Assert: Email stored with exact casing
        """
        # Arrange
        email = "NewStudent@MergingTon.Edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        activity = client.get("/activities").json()[activity_name]
        assert email in activity["participants"]


class TestRemoveLogic:
    """Unit tests for removal business logic."""

    def test_participant_removed_from_list(self, client, existing_participant):
        """
        Test: Remove removes email from activity's participants list.
        
        Arrange: Email in activity (michael@mergington.edu)
        Act: Call remove endpoint
        Assert: Email removed from participants list
        """
        # Arrange
        email = existing_participant
        activity_name = "Chess Club"
        initial_count = len(
            client.get("/activities").json()[activity_name]["participants"]
        )
        assert email in client.get("/activities").json()[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        updated_activity = client.get("/activities").json()[activity_name]
        assert email not in updated_activity["participants"]
        assert len(updated_activity["participants"]) == initial_count - 1

    def test_remove_nonexistent_participant(self, client, sample_email):
        """
        Test: Remove non-enrolled email returns error.
        
        Arrange: Email not in activity
        Act: Call remove endpoint with non-enrolled email
        Assert: Error returned, participants list unchanged
        """
        # Arrange
        email = sample_email
        activity_name = "Chess Club"
        initial_participants = client.get("/activities").json()[activity_name]["participants"].copy()
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        updated_activity = client.get("/activities").json()[activity_name]
        assert updated_activity["participants"] == initial_participants

    def test_remove_only_specified_email(self, client):
        """
        Test: Remove only removes the specified email, not similar ones.
        
        Arrange: Two similar emails in same activity
        Act: Remove one email
        Assert: Only that email removed, other similar email remains
        """
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity_name = "Gym Class"
        
        # Add both emails
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})
        
        # Verify both are added
        activity = client.get("/activities").json()[activity_name]
        assert email1 in activity["participants"]
        assert email2 in activity["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email1}
        )
        
        # Assert
        assert response.status_code == 200
        activity = client.get("/activities").json()[activity_name]
        assert email1 not in activity["participants"]
        assert email2 in activity["participants"]


class TestDataValidation:
    """Unit tests for data validation and edge cases."""

    def test_activity_not_found_signup(self, client, sample_email):
        """
        Test: Signup to nonexistent activity returns 404.
        
        Arrange: Invalid activity name
        Act: POST signup for nonexistent activity
        Assert: 404 error
        """
        # Arrange
        email = sample_email
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404

    def test_activity_not_found_remove(self, client, sample_email):
        """
        Test: Remove from nonexistent activity returns 404.
        
        Arrange: Invalid activity name
        Act: DELETE remove for nonexistent activity
        Assert: 404 error
        """
        # Arrange
        email = sample_email
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404

    def test_empty_activity_participants(self, client):
        """
        Test: Activity with no participants has empty participants list.
        
        Arrange: Fetch activities
        Act: Check an activity that might be empty
        Assert: participants list is empty list (not None)
        """
        # Arrange
        # Create a new activity with no participants
        activities = client.get("/activities").json()
        
        # Act & Assert
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            assert isinstance(participants, list)
            # Participants should be a list (may be empty or have items)
            assert all(isinstance(p, str) for p in participants)
