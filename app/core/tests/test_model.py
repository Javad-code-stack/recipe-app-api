"""
Test for the models
"""

from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email, password=password
        )
        self.assertEqual(user.email, email)
        # we check through hashing system that's why we use assertTrue
        self.assertTrue(user.check_password(password))

    def testnew_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        smple_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['Test4@example.COM', 'Test4@example.com'],
        ]

        for email, excepted in smple_emails:
            user = get_user_model().objects.create_user(email, 'test123')
            self.assertEqual(user.email, excepted)

    def test_new_user_without_email_raises_error(self):
        """Test creating user without email raises value error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_creat_superuser(self):
        """Test creating a new superuser"""

        user = get_user_model().objects.create_superuser('test@example.com', 'test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
