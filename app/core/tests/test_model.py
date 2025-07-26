"""
Test for the models
"""
from decimal import Decimal

# when we want to test more than 1 we have to do this
from core import models
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

    def test_create_recipe(self):
        """Test creating recipe successful"""

        # Create a user so we can assign it to our recipe later as the owner of recipe
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        # Create the recipe useing the model we have
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            description='Sample recipe description',
            time_minutes=5,
            price=Decimal('5.50'),
        )
        # Model supposed to return the title as string so we compare it later
        self.assertEqual(str(recipe), recipe.title)
