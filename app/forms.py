from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, NumberRange, Regexp, Email, Length, EqualTo, ValidationError

from app.tables import Profile

class regist_form(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтверждение пароля', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, field):
        if Profile.query.filter_by(username=field.data).first():
            raise ValidationError('Имя пользователя уже занято')

    def validate_email(self, field):
        if Profile.query.filter_by(email=field.data).first():
            raise ValidationError('Email уже используется')

    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError('Пароли не совпадают')

class login_form(FlaskForm):
    username = StringField('Имя пользователя или Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class settings_form(FlaskForm):
    height = IntegerField('Высота поля:',validators=[DataRequired(),NumberRange(4,30)],default=20)
    width = IntegerField('Ширина поля:',validators=[DataRequired(),NumberRange(4,30)],default=10)
    speed = IntegerField('Скорость падения фигуры:',validators=[DataRequired(),NumberRange(1,99)],default=32)
    I_color = StringField('Цвет I', validators=[Regexp(r'^#[0-9a-fA-F]{6}$')], default='#00ffff')
    O_color = StringField('Цвет O', validators=[Regexp(r'^#[0-9a-fA-F]{6}$')], default='#ee0308')
    T_color = StringField('Цвет T', validators=[Regexp(r'^#[0-9a-fA-F]{6}$')], default='#f3d600')
    L_color = StringField('Цвет L', validators=[Regexp(r'^#[0-9a-fA-F]{6}$')], default='#0065aa')
    J_color = StringField('Цвет J', validators=[Regexp(r'^#[0-9a-fA-F]{6}$')], default='#009b1f')
    S_color = StringField('Цвет S', validators=[Regexp(r'^#[0-9a-fA-F]{6}$')], default='#9d3e89')
    Z_color = StringField('Цвет Z', validators=[Regexp(r'^#[0-9a-fA-F]{6}$')], default='#f28500')
    apply = SubmitField("Принять")
    save = SubmitField("Сохранить")
