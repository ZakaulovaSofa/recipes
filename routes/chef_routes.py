# ─ страницы поваров

from app import app
from flask import render_template
from models import db, Chef


@app.route('/chefs')
def chefs():
    chefs = Chef.query.all()
    return render_template('chefs/chefs.html', chefs=chefs)
