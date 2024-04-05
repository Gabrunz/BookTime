from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully", category="success")
                login_user(user, remember="True")
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect Password!", category="error")
        else:
            flash("Email don't exist", category="error")
        
    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():

    logout_user()
    flash("Logged out successfully", category="success")
    return redirect(url_for("views.home"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():

    if request.method == "POST":
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already in our system", category="error")
        elif len(full_name) < 4:
            flash("Full name must be greater than 4 characters", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 4 characters", category="error")
        elif len(password) < 7:
            flash("Password must be greater than 7 characters", category="error")
        elif password != password2:
            flash("Passwords don't match", category="error")
        else:
            user = User(email=email, full_name=full_name, password=generate_password_hash(password, method="scrypt"))
            db.session.add(user)
            db.session.commit()
            login_user(user, remember="True")
            flash("Account Created!", category="success")
            return redirect(url_for("views.home"))

    return render_template("sign-up.html", user=current_user)

    
