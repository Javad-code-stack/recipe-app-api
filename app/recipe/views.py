"""
Views for the recipe APIs

This module contains viewsets for managing recipe-related API endpoints.
It provides CRUD operations for authenticated users while ensuring proper
authentication and authorization through TokenAuthentication and IsAuthenticated
permissions.

Key Components:
- RecipeViewSet: Main viewset for managing recipes
- Custom queryset filtering: Ensures users only access their own recipes
- Integration with core models and recipe serializers

Input Requirements:
- Authenticated user via TokenAuthentication
- User must be logged in to access any recipe-related endpoints

Security Considerations:
- All operations require valid authentication token
- Users can only access their own recipes
- Built-in Django REST Framework security measures apply

Dependencies:
- core.models.Recipe: Data model definition
- recipe.serializer: Serializers for request/response data conversion
- rest_framework modules: Core DRF functionality
"""

# Import Django REST framework components
from rest_framework.authentication import (
    TokenAuthentication,
)  # Authentication using tokens
from rest_framework.permissions import (
    IsAuthenticated,
)  # Restricts access to authenticated users

from rest_framework import viewsets, mixins, status

from rest_framework.decorators import action
from rest_framework.response import Response

# Import local application components
from core.models import Recipe, Tag, Ingredient  # Database model for storing recipes
from recipe import (
    serializer,
)  # Module containing serializers for converting data between Python/JSON


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs

    Provides full CRUD operations for recipes with automatic authentication
    and ownership filtering. Users can only access recipes they created.

    This viewset inherits from ModelViewSet which automatically provides
    default implementations for GET, POST, PUT, PATCH, and DELETE operations.

    Attributes:
        serializer_class (RecipeSerializer): Serializer for converting between
            Python objects and JSON representations
        queryset (QuerySet): Base queryset for all recipes
        authentication_classes (list): Authentication methods (Token-based)
        permission_classes (list): Access control policies (Must be authenticated)

    Methods:
        get_queryset(): Filters recipes by current authenticated user
        get_serializer_class(): Returns appropriate serializer based on action
    """

    serializer_class = serializer.RecipeDetailSerializer

    # pylint: disable=no-member
    # Django's ORM automatically adds 'objects' manager to model classes
    # This line defines the base queryset for this ViewSet
    queryset = Recipe.objects.all()

    # Configure authentication mechanism - Token-based authentication
    # This ensures each request must include a valid token in the Authorization header
    authentication_classes = [TokenAuthentication]

    # Set access permissions - Only authenticated users can access these APIs
    # Unauthenticated users will receive a 401 Unauthorized response
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes filtered by authenticated user.

        Filters the queryset to only include recipes belonging to the currently
        authenticated user. Results are ordered by creation time (newest first).

        The filtering is done at the database level for efficiency, rather than
        filtering in Python after retrieving all records.

        Returns:
            QuerySet: Filtered list of recipes belonging to the current user
            ordered by descending ID (which effectively sorts by newest first).
        """
        # Filter recipes by current user from the request object
        # Order by descending ID to show newest recipes first
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request.

        Uses a different serializer for list operations vs detailed operations.
        The list operation uses a simpler representation, while detail views use
        a more comprehensive serializer with additional fields.

        This allows us to have different representations for different API endpoints:
        - /api/recipes/ (list view) gets a simplified version
        - /api/recipes/123/ (detail view) gets the full details

        Returns:
            type: The appropriate serializer class based on the request type
        """
        if self.action == "list":
            return serializer.RecipeSerializer
        elif self.action == "upload_image":
            return serializer.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Base viewSet for recipe attributes"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-name")


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    serializer_class = serializer.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""

    serializer_class = serializer.IngredientSerializer
    queryset = Ingredient.objects.all()
