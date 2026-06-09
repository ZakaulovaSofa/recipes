# ─ статьи
# ─ управление статьями (админ)

from app import app
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Article, UserRoleEnum, Comment
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS


@app.route('/articles')
def articles():
    page = request.args.get('page', 1, type=int)
    per_page = 21
    
    pagination = Article.query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template(
        'articles/articles.html',
        articles=pagination.items,
        current_page=page,
        has_next=pagination.has_next,
        total=pagination.total
    )


def get_article_comments(article_id):
    comments = (
        Comment.query
        .filter_by(article_id=article_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    for comment in comments:
        if comment.created_at and comment.updated_at:
            comment.is_edited = (comment.updated_at - comment.created_at).total_seconds() > 1
        else:
            comment.is_edited = False
    return comments


@app.route('/articles/<int:article_id>')
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    comments = get_article_comments(article.id)
    return render_template(
        'articles/article_detail.html',
        article=article,
        comments=comments,
        recipe=None  
    )

# КОММЕНТАРИИ К СТАТЬЯМ

def redirect_back_to_article(article_id):
    next_url = request.form.get('next') or request.referrer
    if next_url:
        return redirect(next_url)
    return redirect(url_for('article_detail', article_id=article_id))


@app.route('/articles/<int:article_id>/comments', methods=['POST'])
@login_required
def add_article_comment(article_id):
    article = Article.query.get_or_404(article_id)
    text = request.form.get('text', '').strip()
    if not text:
        flash('Комментарий не может быть пустым.')
        return redirect_back_to_article(article.id)
    
    comment = Comment(
        user_id=current_user.id,
        article_id=article.id,
        text=text
    )
    db.session.add(comment)
    db.session.commit()
    flash('Комментарий добавлен.')
    return redirect_back_to_article(article.id)


@app.route('/articles/comments/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_article_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        flash('Нет прав для редактирования этого комментария.')
        return redirect_back_to_article(comment.article_id)
    
    text = request.form.get('text', '').strip()
    if not text:
        flash('Комментарий не может быть пустым.')
        return redirect_back_to_article(comment.article_id)
    
    comment.text = text
    comment.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Комментарий обновлён.')
    return redirect_back_to_article(comment.article_id)


@app.route('/articles/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_article_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Проверяем, что комментарий принадлежит статье (не рецепту)
    if not comment.article_id:
        flash('Комментарий не найден.')
        return redirect(url_for('articles'))
    
    # Проверяем права: автор комментария или админ
    if comment.user_id != current_user.id and current_user.role != UserRoleEnum.ADMIN:
        flash('Нет прав для удаления этого комментария.')
        return redirect(url_for('article_detail', article_id=comment.article_id))
    
    article_id = comment.article_id
    db.session.delete(comment)
    db.session.commit()
    flash('Комментарий удалён.')
    return redirect(url_for('article_detail', article_id=article_id))

# АДМИН-ПАНЕЛЬ (Управление статьями)

@app.route('/admin/articles/add', methods=['GET', 'POST'])
@login_required
def admin_add_article():
    if current_user.role != UserRoleEnum.ADMIN:
        abort(403)

    if request.method == 'GET':
        return render_template('articles/article_edit.html', article=None)

    # POST — сохранение новой статьи
    title = request.form.get('title', '').strip()
    text = request.form.get('text', '').strip()
    file = request.files.get('photo')
    
    has_errors = False
    
    # Проверка заголовка
    if not title:
        flash('Название статьи не может быть пустым или состоять только из пробелов.', 'article_title_error')
        has_errors = True
    
    # Проверка текста
    if not text:
        flash('Текст статьи не может быть пустым или состоять только из пробелов.', 'article_text_error')
        has_errors = True
    
    # Проверка фото и СОХРАНЕНИЕ даже при ошибках
    saved_image_url = None
    
    if not file or not file.filename:
        flash('Фото статьи обязательно для загрузки.', 'article_photo_error')
        has_errors = True
    elif not allowed_file(file.filename):
        flash('Неподдерживаемый формат фото. Используйте PNG, JPG, JPEG, GIF или WEBP.', 'article_photo_error')
        has_errors = True
    else:
        # СОХРАНЯЕМ ФОТО СРАЗУ, даже если есть другие ошибки
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'articles', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        saved_image_url = f'/static/uploads/articles/{filename}'
    
    # Если есть ошибки, возвращаем форму с сохранённым фото
    if has_errors:
        return render_template(
            'articles/article_edit.html', 
            article=None,
            form_title=title,
            form_text=text,
            temp_image_url=saved_image_url  # Передаём сохранённое фото
        ), 400
    
    # Если ошибок нет, создаём статью с сохранённым фото
    new_article = Article(
        title=title,
        text=text,
        main_image_url=saved_image_url,
        author_id=current_user.id
    )
    
    db.session.add(new_article)
    db.session.commit()
    flash(f'Статья "{new_article.title}" успешно добавлена!', 'success')
    return redirect(url_for('articles'))


@app.route('/admin/articles/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def article_edit(article_id):
    if current_user.role != UserRoleEnum.ADMIN:
        abort(403)

    article = Article.query.get_or_404(article_id)

    if request.method == 'GET':
        return render_template('articles/article_edit.html', article=article)

    # POST — сохранение изменений
    title = request.form.get('title', '').strip()
    text = request.form.get('text', '').strip()
    
    has_errors = False
    
    # Проверка заголовка
    if not title:
        flash('Название статьи не может быть пустым или состоять только из пробелов.', 'article_title_error')
        has_errors = True
    
    # Проверка текста
    if not text:
        flash('Текст статьи не может быть пустым или состоять только из пробелов.', 'article_text_error')
        has_errors = True
    
    # Проверка фото (только если загружено новое, проверяем формат)
    file = request.files.get('photo')
    if file and file.filename and not allowed_file(file.filename):
        flash('Неподдерживаемый формат фото. Используйте PNG, JPG, JPEG, GIF или WEBP.', 'article_photo_error')
        has_errors = True
    
    if has_errors:
        return render_template(
            'articles/article_edit.html', 
            article=article,
            form_title=title,
            form_text=text
        ), 400
    
    article.title = title
    article.text = text
    
    # Проверяем, загружено ли новое фото
    if file and file.filename and allowed_file(file.filename):
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'articles', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        article.main_image_url = f'/static/uploads/articles/{filename}'

    db.session.commit()
    flash(f'Статья "{article.title}" обновлена!', 'success')
    return redirect(url_for('article_detail', article_id=article.id))

@app.route('/admin/articles/<int:article_id>/delete', methods=['POST'])
@login_required
def admin_delete_article(article_id):
    if current_user.role != UserRoleEnum.ADMIN:
        abort(403)

    article = Article.query.get_or_404(article_id)
    article_title = article.title
    
    db.session.delete(article)
    db.session.commit()
    
    flash(f'Статья "{article_title}" успешно удалена.', 'success')
    return redirect(url_for('articles'))