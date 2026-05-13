# ─ статьи

from app import app
from flask import render_template
from models import db, Article


@app.route('/articles')
def articles():
    articles = Article.query.all()
    return render_template('articles/articles.html', articles=articles)
