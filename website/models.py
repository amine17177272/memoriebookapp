from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length,InputRequired, EqualTo

class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField('Login')

class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    user_name = StringField('User Name', validators=[InputRequired(), Length(min=4, max=25)])
    password1 = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password1')])
    submit = SubmitField('Sign Up')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    user_name = db.Column(db.String(150), unique=True)
    memories = db.relationship('Memorie', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
class Memorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('memorie.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
