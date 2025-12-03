from auth import auth
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from models import User, db
from views import views
from config import Config
import threading
from connect_minio import main as run_minio_import

# Create Flask Instance
app = Flask(__name__)

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

def continuous_minio_import():
    """Function that runs the import repeatedly."""
    while True:
        try:
            run_minio_import()
            # Wait for a period (e.g., 60 minutes) before checking MinIO again
            time.sleep(3600)  # 3600 seconds = 1 hour
        except Exception as e:
            print(f"Error in continuous import thread: {e}")
            time.sleep(600) # Wait 10 mins after failure
            

# Function to load user given its ID
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", user=current_user), 404


# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", user=current_user), 500


# Run the application
if __name__ == "__main__":
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created!")