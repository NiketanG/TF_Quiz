from flask import Flask
from app.config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = "user.register"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    with app.app_context():
        from app.user.routes import user

        app.register_blueprint(user)

    from app.admin.routes import admin

    app.register_blueprint(admin)

    return app
