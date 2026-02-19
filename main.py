from auth import auth
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from models import User, db
from views import views
from config import Config
from datetime import timedelta

# Create Flask Instance
app = Flask(__name__)

# Session Configuration
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Add Database
app.config.from_object(Config)

# Initialize the database with app
db.init_app(app)

# Import Blueprints
app.register_blueprint(views, url_prefix="/")
app.register_blueprint(auth, url_prefix="/")

# Initialize LoginManager for user authentication
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))


# Custom Error Pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", user=current_user), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", user=current_user), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created!")

    app.run(debug=True)