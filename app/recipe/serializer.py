"""
Serializers for recipe APIs

This file contains serializers for converting Recipe model instances to/from
JSON representations used in API requests/responses. It defines two serializers:
- RecipeSerializer: Base serializer with common fields
- RecipeDetailSerializer: Extended serializer with additional detail fields

The serializers handle data validation, transformation, and persistence for
recipe-related API endpoints.
"""

from rest_framework import serializers  # Core module for DRF serializers

from core.models import Recipe  # Import Recipe model from core app


# Importing serializers module from Django REST Framework (DRF)
# Provides base classes and functionality for creating serializers

# Accessing the Recipe model defined in the core application module
# This establishes the connection between the database model and API representation


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe model objects

    Converts between JSON representations and Recipe model instances
    Provides basic fields for recipe management APIs

    Attributes:
        model: The model class being serialized
        fields: List of model fields included in serialization
        read_only_fields: Fields that cannot be modified after creation
    """

    class Meta:
        """
        Metaclass defining serializer configuration

        This meta-class holds configuration settings for the serializer,
        specifying which model to use and which fields to include.
        The meta-class pattern is a standard approach in DRF for configuring
        model serializers.
        """

        model = Recipe  # Model class to serialize
        # Specifies which database model this serializer represents

        fields = ["id", "title", "time_minutes", "price", "link"]  # Fields to include
        # Defines the subset of model fields exposed through the API
        # These represent the most essential information about a recipe

        read_only_fields = ["id"]  # ID field should not be modifiable
        # Prevents clients from changing the primary key of a recipe
        # Ensures data integrity by only allowing ID assignment on creation


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for detailed recipe view

    Extends the base RecipeSerializer to include additional fields
    needed for detailed recipe representation in API responses.

    Inherits all fields and configuration from RecipeSerializer while
    adding specialized fields for detailed views.
    """

    class Meta(RecipeSerializer.Meta):
        """
        Metaclass extending parent serializer configuration

        Inherits and extends the Meta configuration from RecipeSerializer
        to add additional fields required for detailed recipe views.
        This demonstrates how DRF allows building serializer hierarchies
        to support different API response formats.
        """

        fields = RecipeSerializer.Meta.fields + ["description"]
        # Adds 'description' field to the existing set of fields from parent
        # Provides richer information for detailed recipe representation
        # The extension pattern avoids duplication while maintaining flexibility
