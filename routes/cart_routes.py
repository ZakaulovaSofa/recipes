# ─ корзина

from app import app
from flask import render_template
from models import db, Recipe, User, CartItem


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    return render_template('cart/cart.html')
