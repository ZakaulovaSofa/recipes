import os
import uuid
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
from models import db, Recipe, RecipeStep


@app.route('/recipes')
def recipes():
    limit = request.args.get('limit', 9, type=int)
    offset = request.args.get('offset', 0, type=int)
    recipes_query = Recipe.query.order_by(Recipe.created_at.desc())
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


@app.route('/recipes/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template(
        'recipes/recipe_detail.html',
        recipe=recipe
    )
