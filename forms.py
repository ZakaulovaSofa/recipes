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

class ChefForm(FlaskForm):
    name = StringField('Имя повара', validators=[DataRequired(), Length(max=70)])
    description = TextAreaField('Биография / Описание', validators=[DataRequired()])
    image_url = StringField('Ссылка на фото повара', validators=[Length(max=300)])
    tags = StringField('Теги (через запятую)', validators=[DataRequired()])
    submit = SubmitField('Сохранить карточку повара')
