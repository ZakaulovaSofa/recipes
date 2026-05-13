# ─ регистрация
# ─ вход
# ─ выход

from app import app
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User
from forms import AuthForm


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = AuthForm()
    if form.validate_on_submit():
        # Ищем пользователя в базе
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            # СЦЕНАРИЙ 1: Пользователь существует -> ВХОД
            if user.check_password(form.password.data):
                login_user(user)
                flash(f'С возвращением, {user.username}!')
                return redirect(url_for('index'))
            else:
                flash('Неверный пароль для этого пользователя.')
        else:
            # СЦЕНАРИЙ 2: Пользователя нет -> РЕГИСТРАЦИЯ
            new_user = User(username=form.username.data)
            new_user.set_password(form.password.data)

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)  # Сразу логиним после создания
            flash('Аккаунт создан! Добро пожаловать.')
            return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))
