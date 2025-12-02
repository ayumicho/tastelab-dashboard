from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from models import User, db
from werkzeug.security import check_password_hash, generate_password_hash

# Create blueprint for authentication routes
auth = Blueprint("auth", __name__)


# Login route, with both GET and POST methods
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get form data
        email = request.form.get("email")
        password = request.form.get("password")

        # Query user by email
        user = User.query.filter_by(email=email).first()
        if user:
            # Check is password is correct
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))  # Redirect user to home
            else:
                flash("Incorrect password, try again", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


# Logout route
@auth.route("/logout")
@login_required
def logout():
    logout_user()  # log the user out
    return redirect(url_for("auth.login"))  # redirect to login page


# Sign up route, with both GET and POST methods
@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # Get form data
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # Check for existing user, validate input
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        elif len(email) < 12:
            flash("Email must be greater than 12 characters.", category="error")
        elif len(first_name) < 2:
            flash("First name must be greater than 2 characters.", category="error")
        elif len(last_name) < 2:
            flash("Last name must be greater than 2 characters.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 6:
            flash("Password must be at least 6 characters.", category="error")
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(password1, method="pbkdf2:sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)  # log new user in
            flash("Account created!", category="success")
            return redirect(url_for("views.home"))  # redirect to home

    return render_template("signup.html", user=current_user)


# Changing profile route, with both GET and POST methods
@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # Get form data
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        email = request.form.get("email")
        password = request.form.get("password")

        # Query user by email
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if password is correct
            if check_password_hash(user.password, password):
                # Update user's profile information
                user.first_name = first_name
                user.last_name = last_name
                db.session.commit()  # Commit the changes to the database

                flash("Profile updated successfully!", category="success")
                return redirect(url_for("auth.profile"))  # Redirect to profile page
            else:
                flash("Incorrect password, profile update failed.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("profile.html", user=current_user)
