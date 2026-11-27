import os


class Config:
    # SECRET_KEY firma la cookie de sesión. En producción llega desde
    # docker-compose.yml; el valor por defecto solo sirve para trabajar local.
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-secreta")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookies de sesión: JavaScript no puede leerlas (HttpOnly).
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


class DevelopmentConfig(Config):
    DEBUG = True
    # Si existe DATABASE_URL la usa; si no, tu MySQL local de XAMPP.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://root:admin123@localhost/juegos"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
    # En producción la conexión SIEMPRE viene de la variable de entorno.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # pool_pre_ping: antes de usar una conexión guardada, SQLAlchemy revisa
    # que MySQL no la haya cerrado (evita "MySQL server has gone away").
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    # Secure = la cookie solo viaja por HTTPS. Como en clase usamos
    # http://localhost, se controla con una variable (False por defecto).
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
