from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from .config import config

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesión para ver esta página."
login_manager.login_message_category = "warning"


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    from . import models  # noqa: F401

    from .routes import main_bp
    from .auth import auth_bp
    from .api.routes import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # El MySQL del contenedor arranca vacío: creamos las tablas que falten.
    # (En pruebas no, porque los tests crean su propia base en memoria.)
    if not app.config.get("TESTING"):
        with app.app_context():
            db.create_all()
            # Gunicorn arranca con --preload: esta función corre UNA vez en el
            # proceso principal y luego se copia (fork) a cada worker. Cerramos
            # las conexiones abiertas para que cada worker abra las suyas.
            db.engine.dispose()

    return app
