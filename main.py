from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from datetime import timedelta
from dotenv import load_dotenv
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
import os

from app.forms import settings_form, regist_form, login_form
from app.tables import db, Profile, Setting, NowSetting, Score

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise ValueError("Требуется SECRET_KEY в .env файле")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("Требуется DATABASE_URL в .env файле")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=1)
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Войдите для доступ'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'



@login_manager.user_loader
def load_user(user_id):
    return Profile.query.get(int(user_id))

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('menu'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    form = regist_form()
    if form.validate_on_submit():
        user = Profile(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        db.session.flush()
        apply_settings = Setting.create(profile_id=user.id)
        NowSetting.create(profile_id=user.id, settings_id=apply_settings.id)
        login_user(user)
        return redirect(url_for('menu'))
    for field_name, errors in form.errors.items():
        for error in errors:
            flash(error)
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    form = login_form()
    if form.validate_on_submit():
        user = Profile.query.filter(
            (Profile.username == form.username.data)|(Profile.email == form.username.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('menu'))
        else:
            flash('Неверные данные или нет такого профиля', 'bad')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

@app.route('/settings')
@login_required
def settings():
    form = settings_form()
    varients_settings = Setting.query.filter_by(profile_id=current_user.id).all()
    return render_template('settings.html', form=form, varients_settings = varients_settings)

@app.route('/add', methods=['POST'])
@login_required
def settings_post():
    form = settings_form()
    if form.apply.data or form.save.data:
        colors_dict = {
            'I': form.I_color.data,'O': form.O_color.data,
            'T': form.T_color.data,'L': form.L_color.data,
            'J': form.J_color.data,'S': form.S_color.data,
            'Z': form.Z_color.data
        }
        apply_settings = Setting.create(profile_id=current_user.id, height = form.height.data,
            width = form.width.data, speed = form.speed.data, figure_colors = colors_dict)
        flash('Настройки сохранены', 'good')
        if form.apply.data:
            NowSetting.create(profile_id=current_user.id, settings_id=apply_settings.id)
            flash('и приняты', 'good')
    return redirect(url_for('settings'))

@app.route('/get_settings/<int:settings_id>')
@login_required
def get_settings(settings_id):
    sets = Setting.query.get(settings_id)
    return jsonify({
        'height': sets.height,
        'width': sets.width,
        'speed': sets.speed,
        'figure_colors': sets.figure_colors
    })

@app.route('/api/settings/<int:settings_id>', methods=['DELETE'])
@login_required
def del_settings(settings_id):
    setting = Setting.query.get(settings_id)
    if current_user.applied and current_user.applied.settings_id == setting.id:
        return jsonify({'error': 'Нельзя удалить текущие настройки'}), 400
    if setting.delete():
        return jsonify({'message': 'Настройки удалены'}), 200
    else:
        return jsonify({'error': 'Ошибка при удалении'}), 500


@app.route('/api/change_settings')
def change_settings():
    if (not current_user.is_authenticated or not current_user.applied
            or not current_user.applied.settings):
        return jsonify({
            'height': 20,
            'width': 10,
            'speed': 32,
            'figure_colors': {
                "I": "cyan",
                "O": "red",
                "T": "yellow",
                "S": "orange",
                "Z": "purple",
                "J": "blue",
                "L": "green"
            }
        })
    settings = current_user.applied.settings
    return jsonify({
        'height': settings.height,
        'width': settings.width,
        'speed': settings.speed,
        'figure_colors': settings.figure_colors
    })

@app.route('/game')
@login_required
def game():
    return render_template('game.html')

@app.route('/save_score', methods=['POST'])
@login_required
def save_score():
    result = request.get_json()
    print(result.get('game_time'))
    Score.create(
        profile_id=current_user.id,score = int(result.get('score', 0)),
        game_time = int(result.get('game_time', 0))
    )
    return '', 204


@app.route('/top_score')
@login_required
def top_score():
    top_scores = Score.query.options(
        db.joinedload(Score.profile)
    ).order_by(Score.score.desc()).limit(100).all()
    return render_template('top_score.html', scores=top_scores)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)