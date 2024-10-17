from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail  # Import Flask-Mail
from .config import Config
from .models import db
from flask_migrate import Migrate
from .utils import create_default_admin
import os
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Initialize Flask-Mail globally (but not tied to an app instance yet)
mail = Mail()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    print("Username:", os.environ.get('MAIL_USERNAME'))
    print("Password:", os.environ.get('MAIL_PASSWORD'))

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    mail.init_app(app)  # Now associate `mail` with the Flask app

    # Register blueprints
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp
    from .routes.main import bp as main_bp
    from .routes.tasks import bp as tasks_bp
    from .routes.user import bp as user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(user_bp)

    # Define user loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create all tables in the database
    with app.app_context():
        db.create_all()
        create_default_admin()

    return app
