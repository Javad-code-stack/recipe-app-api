"""
Tests for the user API.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """
        Test creating a user is successful

        This method tests the user creation API by sending a POST request.
        It verifies that the user is created successfully by
        checking the response status code and the user's password.
        """
        # Define the user information for testing
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
        # Send a POST request to create a user
        res = self.client.post(CREATE_USER_URL, payload)

        # Verify that the response status code is 201, indicating successful creation
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Retrieve the user object based on email and verify the correctness of the password
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            "name": "Test User"
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'pass',
            "name": "Test User"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_create_token_bad_credentials(self):
        """Test that token is not created if invalid credentials are given.

        This test verifies that a bad password
        results in no token being issued and a 400 Bad Request response.

        Steps:
            1. Create a user with valid credentials
            2. Attempt to obtain a token using an incorrect password
            3. Verify the response status code and content

        No parameters required as this is a test method.
        Returns: None
        """

        # Create test user with known credentials
        create_user(email='test@example.com', password='goodpass')

        # Prepare request payload with incorrect password
        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        # Validate response contains no token and returns 400 status
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test that token is not created if password is blank"""

        create_user(email='test@example.com', password='')
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authenication is required for user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'name': self.user.name, 'email': self.user.email})

    def test_post_me_not_allowed(self):
        """Test Post is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile with valid credentials.

        This test verifies that a PATCH request to the ME_URL endpoint successfully
        updates the authenticated user's profile information, including name and password.
        The test ensures that both the name and password are correctly updated in the
        database and that the HTTP response status is OK.

        Attributes:
            payload (dict): Contains the new name and password for the user.
            res (Response): The HTTP response from the PATCH request.
        """

        payload = {'name': 'new name', 'password': 'password123'}

        # Send PATCH request to update user profile
        res = self.client.patch(ME_URL, payload)

        # Refresh user instance from database to get updated values
        self.user.refresh_from_db()

        # Validate updated name matches expected value
        self.assertEqual(self.user.name, payload['name'])

        # Validate updated password using secure check method
        self.assertTrue(self.user.check_password(payload['password']))

        # Confirm successful HTTP response status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)
