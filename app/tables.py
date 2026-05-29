from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Profile(UserMixin, db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)

    applied = db.relationship('NowSetting', back_populates='profile', uselist=False, cascade='all, delete-orphan')
    settings = db.relationship('Setting', backref='profile', lazy=True, cascade='all, delete-orphan')
    result = db.relationship('Score', back_populates='profile', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Профиль: {self.username}, id: {self.id}, email: {self.email}, password: {self.password_hash}>'

    def set_password(self, password):                               #
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):                             #
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create(cls, **kwargs):
        try:
            profile = cls(**kwargs)
            if cls.query.filter_by(username=profile.username).first():
                print(f'{cls} CRUD C) Имя профиля занято')
                db.session.rollback()
            else:
                db.session.add(profile)
                db.session.commit()
                return profile
        except Exception as e:
            db.session.rollback()
            print(f'{cls} CRUD C) {e}')

class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    height = db.Column(db.Integer, default=20)
    width  = db.Column(db.Integer, default=10)
    speed  = db.Column(db.Integer, default=5)
    figure_colors = db.Column(JSONB, nullable=False, default={
        'I': '#00ffff', 'O': '#ffff00', 'T': '#aa00ff',
        'L': '#ff8800', 'J': '#2244ff', 'S': '#44ff44', 'Z': '#ff4444'
    })

    applied = db.relationship('NowSetting', back_populates='settings', uselist=False)

    def __repr__(self):
        return (f'<Настройки: {self.id}, profile: {self.profile_id}, height: {self.height}, width: {self.width},'
                f' speed: {self.speed}, figure_colors: {self.figure_colors}>')

    @classmethod
    def create(cls, **kwargs):
        try:
            setting = cls(**kwargs)
            db.session.add(setting)
            db.session.commit()
            return setting
        except Exception as e:
            db.session.rollback()
            print(f'{cls} CRUD C) {e}')

    def delete(self):
        try:
            if not self.applied:
                db.session.delete(self)
                db.session.commit()
                return True
        except Exception as e:
            db.session.rollback()
            print(f'{self} CRUD D) {e}')
            return False

class NowSetting(db.Model):
    __tablename__ = 'nowsettings'

    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), primary_key=True)
    settings_id = db.Column(db.Integer, db.ForeignKey('settings.id', ondelete='CASCADE'), nullable=False)

    profile = db.relationship('Profile', back_populates='applied')
    settings = db.relationship('Setting', back_populates='applied')

    def __repr__(self):
        return f'<Выбранные настройки profile: {self.profile_id}, settings: {self.settings_id}>'

    @classmethod
    def create(cls, **kwargs):
        try:
            nowsetting = cls(**kwargs)
            exisset = cls.query.get(nowsetting.profile_id)
            if exisset:
                exisset.settings_id = nowsetting.settings_id
                db.session.commit()
                return exisset
            db.session.add(nowsetting)
            db.session.commit()
            return nowsetting
        except Exception as e:
            db.session.rollback()
            print(f'{cls} CRUD C) {e}')

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    game_time = db.Column(db.Integer, nullable=False)

    profile = db.relationship('Profile', back_populates='result')

    def __repr__(self):
        return f'<Счет profile={self.profile_id} score={self.score} time={self.game_time}s>'

    @classmethod
    def create(cls, **kwargs):
        try:
            score = cls(**kwargs)
            db.session.add(score)
            db.session.commit()
            return score
        except Exception as e:
            db.session.rollback()
            print(f'{cls} CRUD C) {e}')

