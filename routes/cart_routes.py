from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import app
from models import db, Recipe, CartItem


def parse_amount(value):
    if value is None:
        return None
    value = str(value).replace(',', '.').strip()
    try:
        return float(value)
    except ValueError:
        return None


def format_amount(value):
    if value is None:
        return ''
    if float(value).is_integer():
        return str(int(value))
    return str(round(value, 2))


def build_cart_data(user_id):
    cart_items = (
        CartItem.query
        .filter_by(user_id=user_id)
        .join(Recipe, CartItem.recipe_id == Recipe.id)
        .order_by(CartItem.id.desc())
        .all()
    )
    cart_recipes = []

    for cart_item in cart_items:
        recipe = cart_item.recipe
        servings = cart_item.servings or 1
        recipe_ingredients = []
        for ingredient in recipe.ingredients or []:
            name = ingredient.get('name', '').strip()
            unit = ingredient.get('unit', '').strip()
            amount_raw = ingredient.get('amount', '')
            amount_number = parse_amount(amount_raw)
            if amount_number is not None:
                amount_for_servings = amount_number * servings
                amount_text = f'{format_amount(amount_for_servings)} {unit}'.strip()
                numeric_amount = amount_for_servings
            else:
                amount_text = f'{amount_raw} {unit}'.strip()
                numeric_amount = ''
            recipe_ingredients.append({
                'name': name,
                'amount': amount_text,
                'raw_amount': numeric_amount,
                'unit': unit
            })
        cart_recipes.append({
            'id': recipe.id,
            'name': recipe.title,
            'servings': servings,
            'ingredients': recipe_ingredients
        })
    return {
        'recipes': cart_recipes
    }


@app.route('/cart')
@login_required
def cart():
    cart_data = build_cart_data(current_user.id)
    return render_template(
        'cart/cart.html',
        cart=cart_data
    )


@app.route('/cart/recipes/<int:recipe_id>/add', methods=['POST'])
@login_required
def add_to_cart(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    servings = request.form.get('servings', 1, type=int)
    if servings < 1:
        servings = 1
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe.id
    ).first()

    if cart_item:
        cart_item.servings = servings
        flash('Количество порций в корзине обновлено.')
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            recipe_id=recipe.id,
            servings=servings
        )
        db.session.add(cart_item)
        flash('Рецепт добавлен в корзину.')
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/cart/recipes/<int:recipe_id>/servings', methods=['POST'])
@login_required
def update_cart_servings(recipe_id):
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe_id
    ).first_or_404()
    servings = request.form.get('servings', 1, type=int)
    if servings < 1:
        servings = 1

    cart_item.servings = servings
    db.session.commit()
    flash('Количество порций обновлено.')
    return redirect(url_for('cart'))


@app.route('/cart/recipes/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_from_cart(recipe_id):
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe_id
    ).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    flash('Рецепт удалён из корзины.')
    return redirect(url_for('cart'))


@app.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Корзина очищена.')
    return redirect(url_for('cart'))
