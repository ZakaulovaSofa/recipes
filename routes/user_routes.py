from app import app
import uuid
import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User, Recipe, RecipeStatusEnum

ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}


def allowed_file(filename):
    return (
            '.' in filename
            and filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS
    )


def calculate_user_rank(user):
    published_count = Recipe.query.filter_by(
        author_id=user.id,
        status=RecipeStatusEnum.PUBLISHED
    ).count()
    pending_count = Recipe.query.filter_by(
        author_id=user.id,
        status=RecipeStatusEnum.PENDING
    ).count()
    rejected_count = Recipe.query.filter_by(
        author_id=user.id,
        status=RecipeStatusEnum.REJECTED
    ).count()

    score = published_count * 10 + pending_count * 3 - rejected_count * 2
    if score < 10:
        rank = 'Новичок'
    elif score < 30:
        rank = 'Домашний кулинар'
    elif score < 60:
        rank = 'Опытный автор'
    elif score < 100:
        rank = 'Кулинарный эксперт'
    else:
        rank = 'Шеф Be cooking'
    return rank


@app.route('/profile')
@login_required
def profile():
    rank = calculate_user_rank(current_user)

    my_recipes = Recipe.query.filter_by(
        author_id=current_user.id
    ).order_by(
        Recipe.created_at.desc()
    ).limit(3).all()

    return render_template(
        'profile/profile.html',
        user=current_user,
        rank=rank,
        my_recipes=my_recipes
    )


@app.route('/profile/avatar', methods=['POST'])
@login_required
def update_avatar():
    avatar = request.files.get('avatar')
    if not avatar or not avatar.filename:
        flash('Файл не выбран.')
        return redirect(url_for('profile'))
    if not allowed_file(avatar.filename):
        flash('Можно загрузить только png, jpg, jpeg или webp.')
        return redirect(url_for('profile'))
    filename = f"{uuid.uuid4()}_{secure_filename(avatar.filename)}"
    upload_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        'avatars',
        filename
    )
    avatar.save(upload_path)
    current_user.avatar_url = f'/static/uploads/avatars/{filename}'
    db.session.commit()
    flash('Аватар обновлён.')
    return redirect(url_for('profile'))
