# ─ главный файл приложения
# ─ создание Flask-приложения
# ─ подключение БД
# ─ регистрация роутов
# ─ запуск сервера

from flask import Flask, redirect, url_for, request
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView, expose
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


admin = Admin(
    app,
    name='Be cooking admin',
    index_view=SecureAdminIndexView()
)

admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Recipe, db.session))
admin.add_view(SecureModelView(Article, db.session))
admin.add_view(SecureModelView(Chef, db.session))
admin.add_view(SecureModelView(Comment, db.session))
admin.add_view(SecureModelView(RecipeStep, db.session))


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


# Создаем таблицы (в идеале это делать через миграции, но для начала ок)
with app.app_context():
    db.create_all()
    create_initial_admin()

# импорт роутов
from routes.main_routes import *
from routes.recipe_routes import *
from routes.chef_routes import *
from routes.article_routes import *
from routes.auth_routes import *
from routes.user_routes import *
from routes.cart_routes import *

if __name__ == "__main__":
    app.run(debug=True, port=5050)
