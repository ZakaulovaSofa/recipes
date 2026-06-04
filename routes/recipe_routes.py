import os
import uuid
import re
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import app
from models import db, Recipe, RecipeStep, RecipeStatusEnum, Favorite, CartItem, Note, Comment

RECIPE_UNIT_OPTIONS = [
    ('г', 'граммы'),
    ('кг', 'килограммы'),
    ('л', 'литры'),
    ('мл', 'миллилитры'),
    ('ст. л.', 'столовые ложки'),
    ('ч. л.', 'чайные ложки'),
    ('стакан', 'стаканы'),
    ('капля', 'капли'),
    ('щепотка', 'щепотки'),
    ('шт', 'штуки'),
]


def clean_text(value):
    if value is None:
        return ''
    return value.strip()


def get_allowed_recipe_units():
    return {unit_value for unit_value, unit_label in RECIPE_UNIT_OPTIONS}


AMOUNT_PATTERN = re.compile(r'^\s*\d+([.,]\d+)?\s*$|^\s*\d+\s*/\s*\d+\s*$')


def is_valid_ingredient_amount(value):
    if value is None:
        return False
    value = value.strip()
    if not value:
        return False
    if not AMOUNT_PATTERN.match(value):
        return False
    if '/' in value:
        numerator, denominator = value.split('/')
        numerator = numerator.strip()
        denominator = denominator.strip()
        if int(denominator) == 0:
            return False
    return True


def build_ingredients_from_form():
    ingredient_names = request.form.getlist('ingredient_name')
    ingredient_amounts = request.form.getlist('ingredient_amount')
    ingredient_units = request.form.getlist('ingredient_unit')
    allowed_units = get_allowed_recipe_units()
    ingredients = []
    ingredient_errors = {}
    max_len = max(
        len(ingredient_names),
        len(ingredient_amounts),
        len(ingredient_units)
    ) if ingredient_names or ingredient_amounts or ingredient_units else 0

    for i in range(max_len):
        name = clean_text(ingredient_names[i]) if i < len(ingredient_names) else ''
        amount = clean_text(ingredient_amounts[i]) if i < len(ingredient_amounts) else ''
        unit = clean_text(ingredient_units[i]) if i < len(ingredient_units) else ''
        row_errors = {}
        if not name and not amount and not unit:
            row_errors['row'] = 'Заполните строку ингредиента.'
        else:
            if not name:
                row_errors['name'] = 'Укажите название ингредиента.'

            if not amount:
                row_errors['amount'] = 'Укажите количество ингредиента.'
            elif not is_valid_ingredient_amount(amount):
                row_errors['amount'] = 'Количество должно быть числом: например 100, 100.5, 100,5 или 1/2.'

            if not unit:
                row_errors['unit'] = 'Необходимо выбрать единицу измерения.'
            elif unit not in allowed_units:
                row_errors['unit'] = 'Выберите единицу измерения из списка.'
        if row_errors:
            ingredient_errors[i] = row_errors
            continue
        ingredients.append({
            'name': name,
            'amount': amount,
            'unit': unit
        })
    if not ingredients and not ingredient_errors:
        ingredient_errors[0] = {
            'row': 'Добавьте хотя бы один ингредиент.'
        }
    return ingredients, ingredient_errors


def build_ingredient_rows_for_template():
    ingredient_names = request.form.getlist('ingredient_name')
    ingredient_amounts = request.form.getlist('ingredient_amount')
    ingredient_units = request.form.getlist('ingredient_unit')
    rows = []
    max_len = max(
        len(ingredient_names),
        len(ingredient_amounts),
        len(ingredient_units)
    ) if ingredient_names or ingredient_amounts or ingredient_units else 0
    for i in range(max_len):
        rows.append({
            'name': ingredient_names[i] if i < len(ingredient_names) else '',
            'amount': ingredient_amounts[i] if i < len(ingredient_amounts) else '',
            'unit': ingredient_units[i] if i < len(ingredient_units) else ''
        })
    if not rows:
        rows.append({
            'name': '',
            'amount': '',
            'unit': ''
        })
    return rows


def build_steps_from_form():
    step_texts = request.form.getlist('step_descriptions[]')
    step_photos = request.files.getlist('step_images[]')
    steps_data = []
    step_errors = {}
    for index, step_text in enumerate(step_texts):
        text = clean_text(step_text)
        if not text:
            step_errors[index] = 'Описание шага не может быть пустым или состоять только из пробелов.'
            continue
        photo = step_photos[index] if index < len(step_photos) else None
        steps_data.append({
            'text': text,
            'photo': photo,
            'original_index': index
        })
    if not steps_data and not step_errors:
        step_errors[0] = 'Добавьте хотя бы один шаг приготовления.'
    return steps_data, step_errors


def build_step_rows_for_template():
    step_texts = request.form.getlist('step_descriptions[]')
    rows = []
    for step_text in step_texts:
        rows.append({
            'text': step_text,
            'image_url': ''
        })
    if not rows:
        rows.append({
            'text': '',
            'image_url': ''
        })
    return rows


def parse_optional_float(value):
    value = clean_text(value)
    if not value:
        return None

    value = value.replace(',', '.')
    try:
        number = float(value)
    except ValueError:
        return None

    if number < 0:
        return None
    return number


def build_nutrition_from_form():
    nutrition_errors = {}

    calories_raw = request.form.get('calories')
    proteins_raw = request.form.get('proteins')
    fats_raw = request.form.get('fats')
    carbohydrates_raw = request.form.get('carbohydrates')

    calories = parse_optional_float(calories_raw)
    proteins = parse_optional_float(proteins_raw)
    fats = parse_optional_float(fats_raw)
    carbohydrates = parse_optional_float(carbohydrates_raw)

    if clean_text(calories_raw) and calories is None:
        nutrition_errors['calories'] = 'Ккал должны быть положительным числом.'

    if clean_text(proteins_raw) and proteins is None:
        nutrition_errors['proteins'] = 'Белки должны быть положительным числом.'

    if clean_text(fats_raw) and fats is None:
        nutrition_errors['fats'] = 'Жиры должны быть положительным числом.'

    if clean_text(carbohydrates_raw) and carbohydrates is None:
        nutrition_errors['carbohydrates'] = 'Углеводы должны быть положительным числом.'

    return {
        'calories': calories,
        'proteins': proteins,
        'fats': fats,
        'carbohydrates': carbohydrates,
    }, nutrition_errors


def build_nutrition_rows_for_template():
    return {
        'calories': request.form.get('calories', ''),
        'proteins': request.form.get('proteins', ''),
        'fats': request.form.get('fats', ''),
        'carbohydrates': request.form.get('carbohydrates', ''),
    }


def remove_recipe_from_user_collections(recipe_id):
    Favorite.query.filter_by(recipe_id=recipe_id).delete()
    CartItem.query.filter_by(recipe_id=recipe_id).delete()


@app.route('/recipes')
def recipes():
    limit = request.args.get('limit', 20, type=int)
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


def get_recipe_comments(recipe_id):
    comments = (
        Comment.query
        .filter_by(recipe_id=recipe_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    for comment in comments:
        if comment.created_at and comment.updated_at:
            comment.is_edited = (comment.updated_at - comment.created_at).total_seconds() > 1
        else:
            comment.is_edited = False
    return comments


@app.route('/recipes/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if current_user.is_authenticated and recipe.author_id == current_user.id:
        return redirect(url_for('recipe_manage', recipe_id=recipe.id))

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
    comments_allowed = recipe.status == RecipeStatusEnum.PUBLISHED
    comments = get_recipe_comments(recipe.id)
    return render_template(
        'recipes/recipe_detail.html',
        recipe=recipe,
        is_favorite=is_favorite,
        cart_servings=cart_servings,
        is_in_cart=is_in_cart,
        comments=comments,
        comments_allowed=comments_allowed
    )


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


@app.route('/recipes/add', methods=['GET', 'POST'])
@login_required
def recipe_add():
    # GET → просто показать страницу
    if request.method == 'GET':
        return render_template(
            'recipes/recipe_add.html',
            unit_options=RECIPE_UNIT_OPTIONS,
            ingredient_errors={},
            step_errors={},
            nutrition_errors={}
        )

    # POST → создание рецепта
    title = clean_text(request.form.get('title'))
    description = clean_text(request.form.get('description'))
    ingredients, ingredient_errors = build_ingredients_from_form()
    steps_data, step_errors = build_steps_from_form()
    nutrition, nutrition_errors = build_nutrition_from_form()
    has_errors = False
    if not title:
        flash('Название рецепта не может быть пустым или состоять только из пробелов.', 'recipe_title_error')
        has_errors = True
    if not description:
        flash('Описание рецепта не может быть пустым или состоять только из пробелов.', 'recipe_description_error')
        has_errors = True

    if ingredient_errors:
        has_errors = True
    if step_errors:
        has_errors = True
    if nutrition_errors:
        has_errors = True

    if has_errors:
        return render_template(
            'recipes/recipe_add.html',
            unit_options=RECIPE_UNIT_OPTIONS,
            ingredient_errors=ingredient_errors,
            step_errors=step_errors,
            form_ingredients=build_ingredient_rows_for_template(),
            form_steps=build_step_rows_for_template(),
            form_title=request.form.get('title', ''),
            form_description=request.form.get('description', ''),
            form_nutrition=build_nutrition_rows_for_template(),
            nutrition_errors=nutrition_errors
        ), 400

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

    # Создание рецепта
    recipe = Recipe(
        title=title,
        description=description,
        author_id=current_user.id,
        ingredients=ingredients,
        main_image_url=main_image_url,
        calories=nutrition['calories'],
        proteins=nutrition['proteins'],
        fats=nutrition['fats'],
        carbohydrates=nutrition['carbohydrates']
    )
    db.session.add(recipe)
    db.session.commit()

    # Шаги
    for index, step_data in enumerate(steps_data):
        image_url = None
        photo = step_data['photo']

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
            text=step_data['text'],
            image_url=image_url
        )
        db.session.add(step)
    db.session.commit()
    return redirect(url_for('recipe_manage', recipe_id=recipe.id))


@app.route('/recipes/<int:recipe_id>/manage')
@login_required
def recipe_manage(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author_id != current_user.id:
        abort(403)
    comments_allowed = recipe.status == RecipeStatusEnum.PUBLISHED
    comments = get_recipe_comments(recipe.id)
    return render_template(
        'recipes/recipe_manage.html',
        recipe=recipe,
        comments=comments,
        comments_allowed=comments_allowed
    )


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
            RecipeStep=RecipeStep,
            unit_options=RECIPE_UNIT_OPTIONS,
            ingredient_errors={},
            step_errors={},
            nutrition_errors={}
        )

    title = clean_text(request.form.get('title'))
    description = clean_text(request.form.get('description'))
    ingredients, ingredient_errors = build_ingredients_from_form()
    steps_data, step_errors = build_steps_from_form()
    nutrition, nutrition_errors = build_nutrition_from_form()
    has_errors = False

    if not title:
        flash('Название рецепта не может быть пустым или состоять только из пробелов.', 'recipe_title_error')
        has_errors = True
    if not description:
        flash('Описание рецепта не может быть пустым или состоять только из пробелов.', 'recipe_description_error')
        has_errors = True

    if ingredient_errors:
        has_errors = True
    if step_errors:
        has_errors = True
    if nutrition_errors:
        has_errors = True

    if has_errors:
        return render_template(
            'recipes/recipe_edit.html',
            recipe=recipe,
            RecipeStep=RecipeStep,
            unit_options=RECIPE_UNIT_OPTIONS,
            ingredient_errors=ingredient_errors,
            step_errors=step_errors,
            form_ingredients=build_ingredient_rows_for_template(),
            form_steps=build_step_rows_for_template(),
            form_nutrition=build_nutrition_rows_for_template(),
            nutrition_errors=nutrition_errors
        ), 400

    recipe.title = title
    recipe.description = description
    recipe.ingredients = ingredients
    recipe.status = RecipeStatusEnum.PENDING
    recipe.calories = nutrition['calories']
    recipe.proteins = nutrition['proteins']
    recipe.fats = nutrition['fats']
    recipe.carbohydrates = nutrition['carbohydrates']
    remove_recipe_from_user_collections(recipe.id)
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
    RecipeStep.query.filter_by(recipe_id=recipe.id).delete()

    for index, step_data in enumerate(steps_data):
        image_url = None
        photo = step_data['photo']

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
            text=step_data['text'],
            image_url=image_url
        )
        db.session.add(step)
    db.session.commit()
    flash('Рецепт изменён и отправлен на модерацию.')
    return redirect(url_for('recipe_manage', recipe_id=recipe.id))


@app.route('/recipes/<int:recipe_id>/delete', methods=['POST'])
@login_required
def recipe_delete(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author_id != current_user.id:
        abort(403)

    RecipeStep.query.filter_by(recipe_id=recipe.id).delete()
    Note.query.filter_by(recipe_id=recipe_id).delete()
    remove_recipe_from_user_collections(recipe.id)

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
    return redirect(url_for('favorites'))


@app.route('/recipes/<int:recipe_id>/notes')
@login_required
def recipe_notes(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    notes = Note.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe_id
    ).order_by(Note.updated_at.desc()).all()

    return render_template(
        'recipes/recipe_notes.html',
        recipe=recipe,
        notes=notes
    )


@app.route('/recipes/<int:recipe_id>/notes/create', methods=['GET', 'POST'])
@login_required
def create_note(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    if request.method == 'GET':
        return render_template(
            'recipes/note_create.html',
            recipe=recipe,
            note=None
        )

    title = request.form.get('title', '').strip()
    text = request.form.get('text', '').strip()

    if not title or not text:
        flash('Название и текст заметки обязательны для заполнения.')
        return redirect(url_for('create_note', recipe_id=recipe_id))

    note = Note(
        title=title,
        text=text,
        user_id=current_user.id,
        recipe_id=recipe_id
    )

    db.session.add(note)
    db.session.commit()

    flash('Заметка успешно создана!')
    return redirect(url_for('recipe_notes', recipe_id=recipe_id))


@app.route('/notes/<int:note_id>')
@login_required
def view_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    return render_template('recipes/note_detail.html', note=note)


@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        abort(403)

    if request.method == 'GET':
        return render_template(
            'recipes/note_create.html',
            recipe=note.recipe,
            note=note
        )

    title = request.form.get('title', '').strip()
    text = request.form.get('text', '').strip()

    if not title or not text:
        flash('Название и текст заметки обязательны для заполнения.')
        return redirect(url_for('edit_note', note_id=note_id))

    note.title = title
    note.text = text

    db.session.commit()

    flash('Заметка успешно обновлена!')
    return redirect(url_for('recipe_notes', recipe_id=note.recipe_id))


@app.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    recipe_id = note.recipe_id
    db.session.delete(note)
    db.session.commit()
    flash('Заметка успешно удалена!')
    return redirect(url_for('recipe_notes', recipe_id=recipe_id))
