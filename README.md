# recipe-app-api

## Ingredients API Design

- Ability to add ingredients to recipes
- Create model for ingredients
- Add ingredients API
- Update recipe endpoint
    - Create ingredients
    - Manage ingredients

### Ingredients Model

Ingredients model is consists of 2 things:

- name - Name of the ingredient to create
- user - User who owns the ingredient

### Ingredients Endpoint

- api/recipe/ingredients/
    - GET - List of ingredients
- api/recipe/ingredients/<id>/
    - GET - Get ingredient details
    - PUT / PATCH - Update ingredient-
- api/recipe/
    - POST - Create ingredient(as part of a recipe)
- api/recipe/<id>/
    - PUT / PATCH - Create or modify ingredients of a recipe
- 