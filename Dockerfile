# Misma versión de Python que el venv donde se desarrolló el proyecto (3.13)
FROM python:3.13-slim

# No crear archivos .pyc y mostrar los logs al instante en "docker compose logs"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Primero solo las dependencias: Docker guarda esta capa en caché y no
#    reinstala todo cada vez que cambias un .py o un .html
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Después el código
COPY . .

# Usuario sin privilegios: si alguien vulnera la app, no es root
RUN useradd --create-home appuser
USER appuser

ENV FLASK_ENV=production
ENV DATABASE_URL=mysql+pymysql://user:pwd@db/videojuegos

EXPOSE 8000

# 3 workers; --preload crea la app (y las tablas) una sola vez antes de los workers
CMD ["gunicorn", "--workers", "3", "--preload", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "wsgi:app"]
