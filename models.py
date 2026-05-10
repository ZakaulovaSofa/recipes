from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///culinary.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Enum классы
class UserRoleEnum(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class RecipeStatusEnum(enum.Enum):
    PUBLISHED = "published"
    PENDING = "pending"
    REJECTED = "rejected"

# 1. USER
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.USER)
    
    # Связи
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic')
    notes = db.relationship('Note', backref='user', lazy='dynamic')
    chefs = db.relationship('Chef', backref='admin', lazy='dynamic')
    articles = db.relationship('Article', backref='author', lazy='dynamic')

# 2. RECIPE (с полем ingredients: array(JSON))
class Recipe(db.Model):
    __tablename__ = 'recipe'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Enum(RecipeStatusEnum), nullable=False, default=RecipeStatusEnum.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    main_image_url = db.Column(db.String(300))
    
    # array(JSON) - массив JSON объектов
    # Структура: [{"title": "flour", "amount": "200", "unit": "g"}, ...]
    ingredients = db.Column(db.JSON)  # В SQLAlchemy JSON может хранить массивы
    
    # Связи
    steps = db.relationship('RecipeStep', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')

# 3. RECIPE_STEP
class RecipeStep(db.Model):
    __tablename__ = 'recipe_step'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    
    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'step_number', name='unique_recipe_step'),
    )

# 4. ARTICLE
class Article(db.Model):
    __tablename__ = 'article'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    main_image_url = db.Column(db.String(300))
    
    comments = db.relationship('Comment', backref='article', lazy='dynamic', cascade='all, delete-orphan')

# 5. COMMENT
class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=True)

# 6. CHEF (с полем tags: array[string])
class Chef(db.Model):
    __tablename__ = 'chef'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    
    # array(string) - массив строк
    tags = db.Column(db.JSON)  # Хранит массив строк: ["итальянская", "французская"]
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 7. FAVORITE
class Favorite(db.Model):
    __tablename__ = 'favorite'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='unique_favorite'),
    )

# 8. CART_ITEM
class CartItem(db.Model):
    __tablename__ = 'cart_item'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    servings = db.Column(db.Integer, default=1)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='unique_cart_item'),
    )

# 9. NOTE
class Note(db.Model):
    __tablename__ = 'note'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Создание таблиц
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
