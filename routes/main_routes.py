from app import app
from flask import render_template
from models import Recipe


@app.route('/')
@app.route('/index')
def index():
    recipes_query = Recipe.query.order_by(Recipe.created_at.desc())
    recipes = recipes_query.offset(0).limit(9).all()
    return render_template('index.html', recipes=recipes)
