from auth import auth
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from flask_apscheduler import APScheduler
from models import User, db
from views import views
from config import Config

# Create Flask Instance
app = Flask(__name__)

# Add Database
app.config.from_object(Config)

# Initialize the database with app
db.init_app(app)

# Initialize Scheduler
scheduler = APScheduler()

# Import Blueprints
app.register_blueprint(views, url_prefix="/")
app.register_blueprint(auth, url_prefix="/")

# Initialize LoginManager for user authentication
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


# Function to load user given its ID
@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))


# Configure scheduled tasks
def configure_scheduler(app):
    """Configure background tasks"""
    if not app.config.get('SCHEDULER_ENABLED', True):
        return
    
    @scheduler.task('interval', id='sync_minio', minutes=60, max_instances=1, misfire_grace_time=60)
    def scheduled_minio_sync():
        """Run every 60 minutes to check for new MinIO data"""
        with app.app_context():
            try:
                from sync.minio_sync import sync_new_analyses
                # Pass max_imports parameter (None = import all, or set a limit like 10)
                result = sync_new_analyses(max_imports=10)
                app.logger.info(f"Scheduled sync: {result['new_imports']} imported, "
                              f"{result['skipped']} skipped in {result['duration']}s")
            except Exception as e:
                app.logger.error(f"Scheduler error: {e}")
                import traceback
                app.logger.error(traceback.format_exc())
    
    scheduler.init_app(app)
    scheduler.start()
    app.logger.info("Background scheduler started - checking MinIO every 5 minutes")

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
    
    # Start background scheduler
    configure_scheduler(app)
    
    app.run(debug=True)