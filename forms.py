# ─ Flask-WTF формы:
#      регистрация
#      авторизация
#      рецепт
#      статья
#      комментарий

from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *


class AuthForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Продолжить')

