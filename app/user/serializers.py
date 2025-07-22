"""
Serializers for the user API View
"""

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
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

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user

        Args:
            attrs (dict): The attributes to validate, typically includes 'email' and 'password'.

        Returns:
            dict: The validated attributes
            with an additional 'user' key if authentication is successful.

        Raises:
            serializers.ValidationError: If authentication fails with the provided credentials.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        # Attempt to authenticate the user with the provided email and password
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs
