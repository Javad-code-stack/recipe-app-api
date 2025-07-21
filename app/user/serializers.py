"""
Serializers for the user API View
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object

    A serializer is a tool
    that helps turn user data (like email, password, name) into a format (like JSON).

    In simple terms:

        - It reads data from a user (for example, when they sign up).
        - It checks if the data is correct
            (like making sure the password is at least 5 characters long).
        - It saves the data to the database, and makes sure the password is encrypted.
        - It sends back user data without the password when needed.

    ModelSerializer is used instead of the basic Serializer
    because it provides automatic mapping to model fields,
    saving time and reducing boilerplate code.

    Here’s why ModelSerializer and not Serializer:

        - ModelSerializer automatically creates fields based on the model (here, the User model).
        - It simplifies defining common operations like validation and creating instances.
        - You don’t need to manually define each field or its properties if they match the model.
        - It includes built-in support for standard model field types (like email, password, name).
        - a regular Serializer would require you to explicitly define each field and its behavior,
            even if they directly map to the model.
    """

    class Meta:
        """Meta class"""
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """
        Creates and returns a new user instance with an encrypted password.

        This method uses the Django authentication system's create_user method
        to ensure proper password hashing and user creation.

        Parameters:
            validated_data (dict): Dictionary containing validated user data
                Expected keys include 'email', 'password', and other optional
                user profile fields

        Returns:
            User: A new User instance with encrypted password storage
        """
        return get_user_model().objects.create_user(**validated_data)
