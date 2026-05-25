from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from app import app
from models import db, Recipe, RecipeStep, RecipeStatusEnum


def api_error(message, status_code):
    return jsonify({
        "success": False,
        "error": message
    }), status_code


def api_login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return api_error("Необходима авторизация.", 401)
        return view_func(*args, **kwargs)
    return wrapper


def recipe_to_dict(recipe, detailed=False):
    data = {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "status": recipe.status.value,
        "main_image_url": recipe.main_image_url,
        "ingredients": recipe.ingredients or [],
        "author": {
            "id": recipe.author.id,
            "username": recipe.author.username
        },
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None
    }

    if detailed:
        data["steps"] = [
            {
                "id": step.id,
                "step_number": step.step_number,
                "text": step.text,
                "image_url": step.image_url
            }
            for step in recipe.steps.order_by(RecipeStep.step_number).all()
        ]
    return data


def validate_ingredient(ingredient):
    if not isinstance(ingredient, dict):
        return "Каждый ингредиент должен быть JSON-объектом."
    name = ingredient.get("name")
    amount = ingredient.get("amount")
    unit = ingredient.get("unit")

    if not isinstance(name, str) or not name.strip():
        return "У каждого ингредиента должно быть непустое поле name."
    if amount is None:
        return "У каждого ингредиента должно быть поле amount."
    if not isinstance(amount, (str, int, float)):
        return "Поле amount у ингредиента должно быть строкой или числом."
    if not isinstance(unit, str):
        return "Поле unit у ингредиента должно быть строкой."
    return None


def validate_step(step):
    if not isinstance(step, dict):
        return "Каждый шаг должен быть JSON-объектом."
    text = step.get("text")
    if not isinstance(text, str) or not text.strip():
        return "У каждого шага должно быть непустое поле text."
    image_url = step.get("image_url")
    if image_url is not None and not isinstance(image_url, str):
        return "Поле image_url у шага должно быть строкой."
    return None


def validate_recipe_payload(data, partial=False):
    if not isinstance(data, dict):
        return "Тело запроса должно быть JSON-объектом."
    required_fields = ["title", "description", "ingredients", "steps"]
    if not partial:
        for field in required_fields:
            if field not in data:
                return f"Обязательное поле отсутствует: {field}."

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return "Поле title должно быть непустой строкой."
        if len(data["title"].strip()) > 200:
            return "Поле title не должно быть длиннее 200 символов."

    if "description" in data:
        if not isinstance(data["description"], str) or not data["description"].strip():
            return "Поле description должно быть непустой строкой."

    if "main_image_url" in data:
        if data["main_image_url"] is not None and not isinstance(data["main_image_url"], str):
            return "Поле main_image_url должно быть строкой или null."

    if "ingredients" in data:
        if not isinstance(data["ingredients"], list):
            return "Поле ingredients должно быть массивом."
        if len(data["ingredients"]) == 0:
            return "Нужно указать хотя бы один ингредиент."
        for ingredient in data["ingredients"]:
            ingredient_error = validate_ingredient(ingredient)
            if ingredient_error:
                return ingredient_error

    if "steps" in data:
        if not isinstance(data["steps"], list):
            return "Поле steps должно быть массивом."
        if len(data["steps"]) == 0:
            return "Нужно указать хотя бы один шаг приготовления."
        for step in data["steps"]:
            step_error = validate_step(step)
            if step_error:
                return step_error
    return None


@app.route('/api/recipes', methods=['GET'])
def api_get_recipes():
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    status = request.args.get('status')

    if limit < 1 or limit > 100:
        return api_error("Параметр limit должен быть от 1 до 100.", 400)
    if offset < 0:
        return api_error("Параметр offset не может быть отрицательным.", 400)

    recipes_query = Recipe.query
    if status:
        try:
            recipes_query = recipes_query.filter_by(status=RecipeStatusEnum(status))
        except ValueError:
            return api_error("Некорректный статус рецепта.", 400)
    else:
        recipes_query = recipes_query.filter_by(status=RecipeStatusEnum.PUBLISHED)

    total = recipes_query.count()
    recipes = (
        recipes_query
        .order_by(Recipe.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return jsonify({
        "success": True,
        "items": [
            recipe_to_dict(recipe)
            for recipe in recipes
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_next": offset + limit < total,
            "has_prev": offset > 0
        }
    }), 200


@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def api_get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return api_error("Рецепт не найден.", 404)
    return jsonify({
        "success": True,
        "item": recipe_to_dict(recipe, detailed=True)
    }), 200


@app.route('/api/recipes', methods=['POST'])
@api_login_required
def api_create_recipe():
    data = request.get_json(silent=True)
    validation_error = validate_recipe_payload(data, partial=False)
    if validation_error:
        return api_error(validation_error, 400)

    recipe = Recipe(
        title=data["title"].strip(),
        description=data["description"].strip(),
        author_id=current_user.id,
        ingredients=[
            {
                "name": str(ingredient["name"]).strip(),
                "amount": str(ingredient["amount"]).strip(),
                "unit": ingredient["unit"].strip()
            }
            for ingredient in data["ingredients"]
        ],
        main_image_url=data.get("main_image_url"),
        status=RecipeStatusEnum.PENDING
    )
    db.session.add(recipe)
    db.session.commit()
    for index, step_data in enumerate(data["steps"], start=1):
        step = RecipeStep(
            recipe_id=recipe.id,
            step_number=index,
            text=step_data["text"].strip(),
            image_url=step_data.get("image_url")
        )
        db.session.add(step)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Рецепт создан и отправлен на модерацию.",
        "item": recipe_to_dict(recipe, detailed=True)
    }), 201


@app.route('/api/recipes/<int:recipe_id>', methods=['PATCH'])
@api_login_required
def api_update_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return api_error("Рецепт не найден.", 404)
    if recipe.author_id != current_user.id:
        return api_error("Нет прав на изменение этого рецепта.", 403)

    data = request.get_json(silent=True)
    validation_error = validate_recipe_payload(data, partial=True)
    if validation_error:
        return api_error(validation_error, 400)

    if "title" in data:
        recipe.title = data["title"].strip()
    if "description" in data:
        recipe.description = data["description"].strip()
    if "main_image_url" in data:
        recipe.main_image_url = data["main_image_url"]
    if "ingredients" in data:
        recipe.ingredients = [
            {
                "name": str(ingredient["name"]).strip(),
                "amount": str(ingredient["amount"]).strip(),
                "unit": ingredient["unit"].strip()
            }
            for ingredient in data["ingredients"]
        ]
    if "steps" in data:
        RecipeStep.query.filter_by(recipe_id=recipe.id).delete()
        for index, step_data in enumerate(data["steps"], start=1):
            step = RecipeStep(
                recipe_id=recipe.id,
                step_number=index,
                text=step_data["text"].strip(),
                image_url=step_data.get("image_url")
            )
            db.session.add(step)
    recipe.status = RecipeStatusEnum.PENDING
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Рецепт обновлён и отправлен на модерацию.",
        "item": recipe_to_dict(recipe, detailed=True)
    }), 200


@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
@api_login_required
def api_delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return api_error("Рецепт не найден.", 404)
    if recipe.author_id != current_user.id:
        return api_error("Нет прав на удаление этого рецепта.", 403)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Рецепт удалён."
    }), 200
