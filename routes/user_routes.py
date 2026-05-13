# ─ профиль пользователя
from app import app
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.is_authenticated:
        return render_template('profile/profile.html', user=current_user)
    else:
        return redirect(url_for('auth'))
