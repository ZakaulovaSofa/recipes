from datetime import datetime
from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
from models import db, Recipe, Comment


def redirect_back_to_recipe(recipe_id):
    next_url = request.form.get('next') or request.referrer
    if next_url:
        return redirect(next_url)
    return redirect(url_for('recipe_detail', recipe_id=recipe_id))


@app.route('/recipes/<int:recipe_id>/comments', methods=['POST'])
@login_required
def add_recipe_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    text = request.form.get('text', '').strip()
    if not text:
        flash('Комментарий не может быть пустым.')
        return redirect_back_to_recipe(recipe.id)
    comment = Comment(
        user_id=current_user.id,
        recipe_id=recipe.id,
        text=text
    )
    db.session.add(comment)
    db.session.commit()
    return redirect_back_to_recipe(recipe.id)


@app.route('/comments/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        return redirect_back_to_recipe(comment.recipe_id)
    text = request.form.get('text', '').strip()
    if not text:
        flash('Комментарий не может быть пустым.')
        return redirect_back_to_recipe(comment.recipe_id)
    comment.text = text
    comment.updated_at = datetime.utcnow()
    db.session.commit()
    return redirect_back_to_recipe(comment.recipe_id)


@app.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        return redirect_back_to_recipe(comment.recipe_id)
    recipe_id = comment.recipe_id
    db.session.delete(comment)
    db.session.commit()
    return redirect_back_to_recipe(recipe_id)
