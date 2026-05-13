# ─ главный файл приложения
# ─ создание Flask-приложения
# ─ подключение БД
# ─ регистрация роутов
# ─ запуск сервера

from flask import Flask
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import db, User, Recipe, Article, Chef, Comment, RecipeStep
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


# Куда перенаправлять неавторизованных
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


admin = Admin(app, name='Admin panel')

admin.add_view(ModelView(User, db))
admin.add_view(ModelView(Recipe, db))
admin.add_view(ModelView(Article, db))
admin.add_view(ModelView(Chef, db))
admin.add_view(ModelView(Comment, db))
admin.add_view(ModelView(RecipeStep, db))

# Создаем таблицы (в идеале это делать через миграции, но для начала ок)
with app.app_context():
    db.create_all()

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
