from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, LoginForm, SignUpForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user, form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            user_name = form.user_name.data
            password1 = form.password1.data
            password2 = form.password2.data

            user = User.query.filter_by(email=email).first()
            if user:
                message = 'Email already exists.'
                return jsonify({'success': False, 'message': message})
            elif password1 != password2:
                message = 'Passwords do not match.'
                return jsonify({'success': False, 'message': message})
            else:
                new_user = User(email=email, user_name=user_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign-up.html', user=current_user, form=form)