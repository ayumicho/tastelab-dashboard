import os

from auth import auth
from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager, current_user
from models import User, db
from views import views
from reid_blueprint import reid_bp  

# Create Flask Instance
app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///users.db"  # This creates users.db in /app/
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Secret Key - use environment variable for production
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "tastelab")

# Initialize the database with app
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Import Blueprints
app.register_blueprint(views, url_prefix="/")
app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(reid_bp, url_prefix="/reid")

# Initialize LoginManager for user authentication
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


# Function to load user given its ID
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# Create Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", user=current_user), 404


# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", user=current_user), 500


@app.route("/docs/")
@app.route("/docs/<path:path>")
def serve_docs(path="index.html"):
    """Serve Sphinx documentation."""
    docs_dir = os.path.join(app.root_path, "docs", "build", "html")

    if path and not path.endswith(".html"):
        # Handle directories by serving their index.html
        full_path = os.path.join(docs_dir, path, "index.html")
        if os.path.exists(full_path):
            return send_from_directory(docs_dir, os.path.join(path, "index.html"))
    return send_from_directory(docs_dir, path)


# Run the application
if __name__ == "__main__":
    # Important: bind to 0.0.0.0 for Docker
    app.run(host="0.0.0.0", port=3139, debug=False)