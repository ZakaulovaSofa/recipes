import os
import uuid
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import func

from models import db, Chef, UserRoleEnum, ChefRating 

# Импорт приложения должен идти строго до объявления роутов
from app import app

# Настройки для загрузки изображений
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Безопасное извлечение расширения файла."""
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def adapt_chef_for_template(chef):
    """Виртуально прокидывает поля из БД под имена в готовых HTML шаблонах."""
    if chef:
        chef.photo_url = chef.image_url
        chef.bio = chef.description
        
        # Используем существующий relationship 'ratings'
        avg_rating = db.session.query(func.avg(ChefRating.rating)).filter(ChefRating.chef_id == chef.id).scalar()
        chef.average_rating = round(avg_rating, 1) if avg_rating else 0.0

        # Проверяем, оставлял ли текущий авторизованный пользователь оценку
        chef.user_rating = None
        if current_user.is_authenticated:
            existing_rating = chef.ratings.filter_by(user_id=current_user.id).first()
            if existing_rating:
                chef.user_rating = existing_rating.rating
                
    return chef

@app.route('/chefs/<int:chef_id>/rate', methods=['POST'])
@login_required
def rate_chef(chef_id):
    """Добавление, изменение или удаление оценки повара."""
    chef = Chef.query.get_or_404(chef_id)
    action = request.form.get('action', 'save') 

    # Поиск существующей оценки текущего пользователя через relationship
    existing_rating = chef.ratings.filter_by(user_id=current_user.id).first()

    # Удаление оценки
    if action == 'delete':
        if existing_rating:
            db.session.delete(existing_rating)
            db.session.commit()
            flash('Ваша оценка успешно удалена.', 'success')
        return redirect(url_for('chef_profile', chef_id=chef.id))

    # Сохранение или обновление оценки
    rating_raw = request.form.get('rating')
    if not rating_raw or not rating_raw.isdigit():
        flash('Выберите корректное количество звезд.', 'danger')
        return redirect(url_for('chef_profile', chef_id=chef.id))
        
    rating_val = int(rating_raw)
    if rating_val < 1 or rating_val > 5:
        flash('Оценка должна быть от 1 до 5.', 'danger')
        return redirect(url_for('chef_profile', chef_id=chef.id))

    if existing_rating:
        existing_rating.rating = rating_val
        flash('Ваша оценка успешно изменена!', 'success')
    else:
        new_rating = ChefRating(chef_id=chef.id, user_id=current_user.id, rating=rating_val)
        db.session.add(new_rating)
        flash('Оценка успешно сохранена!', 'success')

    db.session.commit()
    return redirect(url_for('chef_profile', chef_id=chef.id))


# ==========================================
# ПОЛЬЗОВАТЕЛЬСКАЯ ЧАСТЬ (Публичный просмотр)
# ==========================================

@app.route('/chefs')
def chefs():
    """Просмотр списка всех поваров с пагинацией и фильтрацией по категориям."""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', type=str)
    per_page = 6
    
    query = Chef.query.order_by(Chef.created_at.desc())
    
    if category:
        query = query.filter(Chef.tags.contains(category.lower()))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    adapted_chefs = [adapt_chef_for_template(c) for c in pagination.items]
    
    return render_template(
        'chefs/chefs.html', 
        chefs=adapted_chefs,
        current_page=page,
        has_next=pagination.has_next,
        current_category=category
    )

@app.route('/chefs/<int:chef_id>')
def chef_profile(chef_id):
    """
    Детальная страница повара с динамическим разделением прав.
    И для обычного пользователя, и для админа отдаем один объединенный шаблон.
    Разделение элементов управления происходит внутри самого HTML-файла.
    """
    chef = Chef.query.get_or_404(chef_id)
    adapted_chef = adapt_chef_for_template(chef)
    
    # Возвращаем один шаблон для всех (кнопки админа теперь внутри chef_profile.html)
    return render_template('chefs/chef_profile.html', chef=adapted_chef)

# ==========================================
# АДМИН-ПАНЕЛЬ (Управление поварами)
# ==========================================

@app.route('/admin/chefs/add', methods=['GET', 'POST'])
@login_required
def admin_add_chef():
    """Создание карточки повара в админке."""
    if current_user.role != UserRoleEnum.ADMIN:
        abort(403)

    if request.method == 'GET':
        return render_template('chefs/chef_edit.html', chef=None)

    # POST — сохранение нового повара
    name = request.form.get('name')
    bio = request.form.get('bio')
    
    tags = request.form.getlist('tags[]')
    tag_list = [t.strip().lower() for t in tags if t.strip()]

    image_url = '/static/img/default_chef.jpg'
    file = request.files.get('photo')
    
    if file and file.filename:
        if allowed_file(file.filename):
            filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chefs', filename)
            
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)
            image_url = f'/static/uploads/chefs/{filename}'

    new_chef = Chef(
        name=name,
        description=bio,
        image_url=image_url,
        tags=tag_list,
        user_id=current_user.id
    )
    
    db.session.add(new_chef)
    db.session.commit()
    flash(f'Повар {new_chef.name} успешно добавлен!', 'success')
    return redirect(url_for('chefs'))

@app.route('/admin/chefs/<int:chef_id>/edit', methods=['GET', 'POST'])
@login_required
def chef_edit(chef_id):
    """Редактирование карточки повара (внешний вид аналогичен admin_add_chef)."""
    if current_user.role != UserRoleEnum.ADMIN:
        abort(403)

    chef = Chef.query.get_or_404(chef_id)

    if request.method == 'GET':
        return render_template('chefs/chef_edit.html', chef=adapt_chef_for_template(chef))

    # POST — сохранение изменений
    chef.name = request.form.get('name')
    chef.description = request.form.get('bio')
    
    tags = request.form.getlist('tags[]')
    chef.tags = [t.strip().lower() for t in tags if t.strip()]

    file = request.files.get('photo')
    if file and file.filename:
        if allowed_file(file.filename):
            filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chefs', filename)
            
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)
            chef.image_url = f'/static/uploads/chefs/{filename}'

    db.session.commit()
    flash(f'Профиль {chef.name} обновлен!', 'success')
    # Перенаправляем на исправленный эндпоинт chef_profile
    return redirect(url_for('chef_profile', chef_id=chef.id))

@app.route('/admin/chefs/<int:chef_id>/delete', methods=['POST'])
@login_required
def admin_delete_chef(chef_id):
    """Удаление карточки повара администратором."""
    if current_user.role != UserRoleEnum.ADMIN:
        abort(403)

    chef = Chef.query.get_or_404(chef_id)
    chef_name = chef.name
    
    db.session.delete(chef)
    db.session.commit()
    
    flash(f'Повар {chef_name} успешно удален.', 'success')
    return redirect(url_for('chefs'))


