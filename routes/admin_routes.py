# ─ админ-панель
# ─ модерация рецептов
# ─ добавление статей
# ─ добавление поваров

import json
from flask import redirect, url_for, request
from flask_login import current_user
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import StringField
from sqlalchemy.orm.attributes import flag_modified  # <-- ДОБАВИЛИ ВАЖНЫЙ ИМПОРТ ДЛЯ РАБОТЫ JSON
from models import Chef, UserRoleEnum

# Перенесли защищенные вьюхи сюда, чтобы убрать зависимость от app.py
class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return (
                current_user.is_authenticated
                and current_user.role == UserRoleEnum.ADMIN
        )

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth', next=request.url))


class SecureModelView(ModelView):
    def is_accessible(self):
        return (
                current_user.is_authenticated
                and current_user.role == UserRoleEnum.ADMIN
        )

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth', next=request.url))


class ChefModelView(SecureModelView):
    """Кастомная админка для поваров с удобным вводом тегов."""
    column_list = ('name', 'tags', 'created_at')
    column_searchable_list = ('name',)
    
    # Подменяем поле ввода на обычную текстовую строку
    form_overrides = {
        'tags': StringField
    }
    
    # Красивые лейблы для полей формы
    form_args = {
        'name': {'label': 'ФИО повара'},
        'description': {'label': 'Биография / Информация'},
        'image_url': {'label': 'Ссылка на фото (или путь к файлу)'},
        'tags': {
            'label': 'Теги (через запятую)',
            'description': 'Введите теги через запятую, например: французская, десерты, шеф'
        },
        'admin': {'label': 'Кто добавил (Администратор)'}
    }

    def create_form(self, obj=None):
        """Очищаем поле тегов при создании новой карточки, чтобы не было пустых скобок."""
        form = super(ChefModelView, self).create_form(obj)
        if form.tags.data is None or form.tags.data == '[]':
            form.tags.data = ''
        return form

    def edit_form(self, obj=None):
        """Преобразуем теги из БД в чистую строку для формы, защищая от любых ошибок типа данных."""
        form = super(ChefModelView, self).edit_form(obj) # <-- ИСПРАВИЛИ ОТСТУПЫ ЗДЕСЬ
        
        if obj and obj.tags:
            # Сценарий 1: В базе лежит правильный список (list)
            if isinstance(obj.tags, list):
                form.tags.data = ', '.join(obj.tags)
            
            # Сценарий 2: В базе лежит строка (например, из-за старых ошибок сохранения)
            elif isinstance(obj.tags, str):
                # Мягко вычищаем любые квадратные скобки и кавычки, если они записались как текст
                clean_str = obj.tags.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
                form.tags.data = clean_str
                
        return form

    def on_model_change(self, form, model, is_created):
        """Конвертируем строку тегов обратно в чистый JSON-список перед сохранением в БД."""
        if form.tags.data and isinstance(form.tags.data, str):
            # Тотальная очистка от мусорных скобок и кавычек перед разбивкой на элементы
            raw_data = form.tags.data.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
            
            # Формируем чистый массив строк
            tag_list = [t.strip().lower() for t in raw_data.split(',') if t.strip()]
            model.tags = tag_list
        else:
            model.tags = []
            
        # Принудительно заставляем SQLAlchemy зафиксировать изменения в сессии
        flag_modified(model, 'tags')


def init_admin_views(admin, db):
    """Функция для регистрации вьюхи без циклического импорта."""
    admin.add_view(ChefModelView(Chef, db.session))
