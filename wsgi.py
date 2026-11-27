"""Punto de entrada para Gunicorn.

Gunicorn necesita una VARIABLE con la aplicación ("wsgi:app"), pero nuestro
paquete app/ solo tiene la FUNCIÓN create_app(). Aquí la llamamos una vez.
FLASK_ENV (definida en el Dockerfile) elige la configuración: production.
"""
import os

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))
