"""
Tests for the Ingredient API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializer import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Return URL for ingredient detail"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="testPass123"):
    """Create and return a new user with given email and password."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientAPITests(TestCase):
    """Test unauthenticated users API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authenticated users API"""

    # ! Creating an authenticated user
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients"""
        Ingredient.objects.create(user=self.user, name="salt")
        Ingredient.objects.create(user=self.user, name="pepper")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are limited to user"""
        # ! Unauthenticated user
        user2 = create_user(email="user2@example.com", password="testPass123")
        Ingredient.objects.create(user=user2, name="milk")
        ingredient = Ingredient.objects.create(user=self.user, name="wine")

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredients(self):
        """Test updating ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name="rice")

        payload = {"name": "brown rice"}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test deleting ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name="blue salt")

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        """
            here we get the list of ingredients for this user.
            since he just created one ingredient and deleted that,
            there is no more ingredient left in his list and the last line shows it.
        """
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
