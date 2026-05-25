# ─ главного файл приложения
# ─ создание Flask-приложения
# ─ подключение БД
# ─ регистрация роутов
# ─ запуск сервера

from flask import Flask, redirect, url_for, request
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from models import db, User, Recipe, Article, Chef, Comment, RecipeStep, UserRoleEnum
import os

app = Flask(__name__)

# конфиг
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///culinary.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Переносим импорт функции инициализации и защищенных представлений СЮДА.
# Теперь admin_routes.py не делает импорты из app.py, что полностью решает проблему Circular Import.
from routes.admin_routes import SecureAdminIndexView, SecureModelView, init_admin_views

admin = Admin(
    app,
    name='Be cooking admin',
    index_view=SecureAdminIndexView()
)

# Стандартные представления таблиц (Заменили db.session на db, чтобы убрать DeprecationWarning)
admin.add_view(SecureModelView(User, db))
admin.add_view(SecureModelView(Recipe, db))
admin.add_view(SecureModelView(Article, db))

# Подключаем кастомную админку для поваров из модуля admin_routes
init_admin_views(admin, db)

# Продолжение стандартных таблиц
admin.add_view(SecureModelView(Comment, db))
admin.add_view(SecureModelView(RecipeStep, db))


def create_initial_admin():
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_username or not admin_password:
        return

    existing_admin = User.query.filter_by(username=admin_username).first()
    if existing_admin:
        existing_admin.role = UserRoleEnum.ADMIN
        db.session.commit()
        return
    admin_user = User(
        username=admin_username,
        role=UserRoleEnum.ADMIN
    )
    admin_user.set_password(admin_password)
    db.session.add(admin_user)
    db.session.commit()


# Создаем таблицы
with app.app_context():
    db.create_all()
    create_initial_admin()


# Контекстный процессор для Jinja2 (Добавьте перед импортом роутов)
@app.context_processor
def inject_enums():
    """Делает перечисление UserRoleEnum доступным во всех HTML-шаблонах."""
    return dict(UserRoleEnum=UserRoleEnum)


# импорт роутов
from routes.main_routes import *
from routes.recipe_routes import *
from routes.chef_routes import *
from routes.article_routes import *
from routes.auth_routes import *
from routes.user_routes import *
from routes.cart_routes import *
from routes.api_recipe_routes import *

if __name__ == "__main__":
    app.run(debug=True, port=5050)
