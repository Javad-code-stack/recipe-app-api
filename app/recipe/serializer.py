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

from core.models import Recipe, Tag  # Import Recipe model from core app


# Importing serializers module from Django REST Framework (DRF)
# Provides base classes and functionality for creating serializers

# Accessing the Recipe model defined in the core application module
# This establishes the connection between the database model and API representation


class TagSerializer(serializers.ModelSerializer):
    """
    TagSerializer
    -------------
    Description: Serializer for converting Tag model instances to/from JSON format.
    This serializer handles the conversion of Tag objects for API requests and responses,
    allowing tags to be created, read, updated, and deleted through the API.

    Parameters: None
    Returns: None
    """

    class Meta:
        """
        Meta
        ----
        Description: Configuration class that tells Django REST Framework how to
        create the serializer. It specifies which model to use, which fields to include,
        and which fields should be read-only.

        Parameters: None
        Returns: None
        """

        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """
    RecipeSerializer
    ----------------
    Description: Serializer for converting Recipe model instances to/from JSON format.
    This serializer handles the conversion of Recipe objects for API requests and responses,
    allowing recipes to be created, read, updated, and deleted through the API. It includes
    basic fields needed for recipe management.

    Parameters: None
    Returns: None
    """

    # Nested serializer for tags - allows tags to be included with recipes
    tags = TagSerializer(many=True, required=False)

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

        fields = [
            "id",
            "title",
            "time_minutes",
            "price",
            "link",
            "tags",
        ]  # Fields to include
        # Defines the subset of model fields exposed through the API
        # These represent the most essential information about a recipe

        read_only_fields = ["id"]  # ID field should not be modifiable
        # Prevents clients from changing the primary key of a recipe
        # Ensures data integrity by only allowing ID assignment on creation

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed"""
        # We get the authenticated user
        auth_user = self.context["request"].user
        # Loop through the tags we pop - either create a new tag or retrieve it
        for tag in tags:
            tag_obj, create = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """
        Create
        ------
        Description: Creates a new Recipe instance with the provided validated data.
        This method handles the creation of recipes, including associating tags with
        the recipe and ensuring tags are created or retrieved as needed.

        Parameters:
        - validated_data (dict): Dictionary containing the cleaned data from the serializer

        Returns:
        - Recipe: The newly created Recipe instance with all associated tags

        Algorithm:
        1. Extract tags from the validated data
        2. Create a new recipe with the remaining data
        3. Get the authenticated user from the request context
        4. For each tag, either create a new tag or retrieve an existing one
        5. Associate each tag with the recipe
        6. Return the created recipe
        """
        # Remove tags from validated_data and assign it to a variable called 'tags'
        tags = validated_data.pop("tags", [])
        # With the rest of the data(except tags) we create a new recipe
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Update
        ------
        """
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    RecipeDetailSerializer
    ----------------------
    Description: Serializer for detailed recipe views. This extends the base
    RecipeSerializer to include additional fields needed for detailed recipe
    representation in API responses. It provides a more comprehensive view
    of recipe information including the description field.

    Parameters: None
    Returns: None

    Inheritance: Extends RecipeSerializer to reuse its functionality while adding
    additional fields for detailed views
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
