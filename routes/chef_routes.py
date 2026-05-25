import os
import uuid
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from models import db, Chef, UserRoleEnum

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
    return chef

# Импортируем app локально, чтобы избежать циклического импорта при старте
from app import app

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
