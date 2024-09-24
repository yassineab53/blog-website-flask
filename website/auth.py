from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db 
from .models import User 
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from validate_email import validate_email

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':   
        email = request.form.get("email")
        password = request.form.get("password")
        if not validate_email(email):
            flash('email invalide.', category='error')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                # Check the password against the hashed password in the database
                if check_password_hash(user.password, password):
                    flash('vous êtes connectés !', category="success")
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('password incorrect .', category='error')
    return render_template("login.html", user=current_user)

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        if email_exists:
            flash('Email déjà utilisé. ', category='error')
        elif username_exists:
            flash('Username déjà utilisé. ', category='error')
        elif password1 != password2:
            flash('essayez une autre fois avec le même password! ', category='error')
            return redirect(url_for('auth.sign_up'))    
        if len(username) < 2:
            flash('Username est trop court . ', category='error')
        elif len(password1) < 6:
            flash('password est trop court! ', category='error')
        elif len(email) < 4:
            flash('Email est invalide. ', category='error')    
        else:
            # Use pbkdf2:sha256 for password hashing
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='pbkdf2:sha256')) 
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User crée!' , category="success")
            return redirect(url_for('views.home'))
    
    return render_template("signup.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
