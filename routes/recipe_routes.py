import os
import uuid
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import app
from models import db, Recipe, RecipeStep, RecipeStatusEnum, Favorite, CartItem


# GET /recipes?limit=X&offset=Y
@app.route('/recipes')
def recipes():
    limit = request.args.get('limit', 9, type=int)
    offset = request.args.get('offset', 0, type=int)
    recipes_query = Recipe.query.filter_by(
        status=RecipeStatusEnum.PUBLISHED
    ).order_by(Recipe.created_at.desc())
    total = recipes_query.count()
    recipes = recipes_query.offset(offset).limit(limit).all()
    has_next = offset + limit < total
    has_prev = offset > 0

    return render_template(
        'recipes/recipes.html',
        recipes=recipes,
        limit=limit,
        offset=offset,
        has_next=has_next,
        has_prev=has_prev
    )


# GET /recipes/{recipeId}
@app.route('/recipes/<int:recipe_id>')
@app.route('/recipes/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    is_favorite = False
    cart_servings = 1
    is_in_cart = False

    if current_user.is_authenticated:
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            recipe_id=recipe.id
        ).first()
        is_favorite = favorite is not None
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            recipe_id=recipe.id
        ).first()
        if cart_item:
            is_in_cart = True
            cart_servings = cart_item.servings or 1

    return render_template(
        'recipes/recipe_detail.html',
        recipe=recipe,
        is_favorite=is_favorite,
        cart_servings=cart_servings,
        is_in_cart=is_in_cart
    )


# GET /my-recipes
@app.route('/my-recipes')
@login_required
def my_recipes():
    limit = request.args.get('limit', 9, type=int)
    offset = request.args.get('offset', 0, type=int)
    status = request.args.get('status')

    recipes_query = Recipe.query.filter_by(
        author_id=current_user.id
    )
    if status:
        try:
            recipes_query = recipes_query.filter_by(
                status=RecipeStatusEnum(status)
            )
        except ValueError:
            flash('Некорректный статус рецепта.')
            return redirect(url_for('my_recipes'))

    recipes_query = recipes_query.order_by(Recipe.created_at.desc())
    total = recipes_query.count()
    my_recipes = recipes_query.offset(offset).limit(limit).all()
    has_next = offset + limit < total
    has_prev = offset > 0
    status_labels = {
        'published': 'Опубликованные',
        'pending': 'На модерации',
        'rejected': 'Отклонённые'
    }

    return render_template(
        'my_recipes/my_recipes.html',
        my_recipes=my_recipes,
        limit=limit,
        offset=offset,
        has_next=has_next,
        has_prev=has_prev,
        current_status=status,
        status_labels=status_labels
    )


# POST /recipes
@app.route('/recipes/add', methods=['GET', 'POST'])
@login_required
def recipe_add():
    # GET → просто показать страницу
    if request.method == 'GET':
        return render_template('recipes/recipe_add.html')

    # POST → создание рецепта
    title = request.form.get('title')
    description = request.form.get('description')
    main_photo = request.files.get('main_photo')
    main_image_url = None

    if main_photo and main_photo.filename:
        filename = f"{uuid.uuid4()}_{secure_filename(main_photo.filename)}"

        upload_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            'recipes',
            filename
        )
        main_photo.save(upload_path)
        main_image_url = f'/static/uploads/recipes/{filename}'

    # Ингредиенты
    ingredient_names = request.form.getlist('ingredient_name')
    ingredient_amounts = request.form.getlist('ingredient_amount')
    ingredient_units = request.form.getlist('ingredient_unit')
    ingredients = []

    for i in range(len(ingredient_names)):
        if ingredient_names[i].strip():
            ingredients.append({
                "name": ingredient_names[i],
                "amount": ingredient_amounts[i],
                "unit": ingredient_units[i]
            })

    # Создание рецепта
    recipe = Recipe(
        title=title,
        description=description,
        author_id=current_user.id,
        ingredients=ingredients,
        main_image_url=main_image_url
    )
    db.session.add(recipe)
    db.session.commit()

    # Шаги
    step_texts = request.form.getlist('step_descriptions[]')
    step_photos = request.files.getlist('step_images[]')

    for index, step_text in enumerate(step_texts):
        image_url = None
        if index < len(step_photos):
            photo = step_photos[index]
            if photo and photo.filename:
                filename = f"{uuid.uuid4()}_{secure_filename(photo.filename)}"
                upload_path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    'recipe_steps',
                    filename
                )
                photo.save(upload_path)
                image_url = f'/static/uploads/recipe_steps/{filename}'

        step = RecipeStep(
            recipe_id=recipe.id,
            step_number=index + 1,
            text=step_text,
            image_url=image_url
        )
        db.session.add(step)
    db.session.commit()
    flash('Рецепт успешно создан!')
    return redirect(url_for('recipe_detail', recipe_id=recipe.id))


# GET /my-recipes/{recipeId}
@app.route('/recipes/<int:recipe_id>/manage')
@login_required
def recipe_manage(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author_id != current_user.id:
        abort(403)
    return render_template(
        'recipes/recipe_manage.html',
        recipe=recipe
    )


# PATCH /recipes/{recipeId}
@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def recipe_edit(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author_id != current_user.id:
        abort(403)
    if request.method == 'GET':
        return render_template(
            'recipes/recipe_edit.html',
            recipe=recipe,
            RecipeStep=RecipeStep
        )

    recipe.title = request.form.get('title')
    recipe.description = request.form.get('description')
    recipe.status = RecipeStatusEnum.PENDING
    main_photo = request.files.get('main_photo')
    if main_photo and main_photo.filename:
        filename = f"{uuid.uuid4()}_{secure_filename(main_photo.filename)}"
        upload_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            'recipes',
            filename
        )
        main_photo.save(upload_path)
        recipe.main_image_url = f'/static/uploads/recipes/{filename}'
    ingredient_names = request.form.getlist('ingredient_name')
    ingredient_amounts = request.form.getlist('ingredient_amount')
    ingredient_units = request.form.getlist('ingredient_unit')
    ingredients = []
    for i in range(len(ingredient_names)):
        if ingredient_names[i].strip():
            ingredients.append({
                "name": ingredient_names[i],
                "amount": ingredient_amounts[i],
                "unit": ingredient_units[i]
            })
    recipe.ingredients = ingredients
    RecipeStep.query.filter_by(recipe_id=recipe.id).delete()
    step_texts = request.form.getlist('step_descriptions[]')
    step_photos = request.files.getlist('step_images[]')
    for index, step_text in enumerate(step_texts):
        if not step_text.strip():
            continue
        image_url = None
        if index < len(step_photos):
            photo = step_photos[index]
            if photo and photo.filename:
                filename = f"{uuid.uuid4()}_{secure_filename(photo.filename)}"
                upload_path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    'recipe_steps',
                    filename
                )
                photo.save(upload_path)
                image_url = f'/static/uploads/recipe_steps/{filename}'
        step = RecipeStep(
            recipe_id=recipe.id,
            step_number=index + 1,
            text=step_text,
            image_url=image_url
        )
        db.session.add(step)
    db.session.commit()
    flash('Рецепт изменён и отправлен на модерацию.')
    return redirect(url_for('recipe_manage', recipe_id=recipe.id))


# DELETE /recipes/{recipeId}
@app.route('/recipes/<int:recipe_id>/delete', methods=['POST'])
@login_required
def recipe_delete(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author_id != current_user.id:
        abort(403)
    db.session.delete(recipe)
    db.session.commit()
    flash('Рецепт удалён.')
    return redirect(url_for('my_recipes'))


@app.route('/recipes/<int:recipe_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe.id
    ).first()

    if favorite:
        db.session.delete(favorite)
        flash('Рецепт удалён из избранного.')
    else:
        favorite = Favorite(
            user_id=current_user.id,
            recipe_id=recipe.id
        )
        db.session.add(favorite)
        flash('Рецепт добавлен в избранное.')
    db.session.commit()
    return redirect(url_for('recipe_detail', recipe_id=recipe.id))


@app.route('/favorites')
@login_required
def favorites():
    limit = request.args.get('limit', 9, type=int)
    offset = request.args.get('offset', 0, type=int)
    favorites_query = (
        Recipe.query
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    total = favorites_query.count()
    favorite_recipes = favorites_query.offset(offset).limit(limit).all()

    has_next = offset + limit < total
    has_prev = offset > 0
    return render_template(
        'favorites/favorites.html',
        favorites=favorite_recipes,
        limit=limit,
        offset=offset,
        has_next=has_next,
        has_prev=has_prev
    )


@app.route('/recipes/<int:recipe_id>/favorite/remove', methods=['POST'])
@login_required
def remove_favorite(recipe_id):
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe_id
    ).first_or_404()
    db.session.delete(favorite)
    db.session.commit()
    flash('Рецепт удалён из избранного.')
    return redirect(url_for('favorites'))
