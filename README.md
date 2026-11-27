# Videojuegos – Despliegue en producción con Docker

Microaplicación Flask para administrar un catálogo de videojuegos, con registro e inicio de sesión de usuarios (Flask-Login), CRUD de juegos y una API REST (`/api/juegos`). En producción se sirve con **Gunicorn** y usa **MySQL 8**, cada uno en su propio contenedor y orquestados con **Docker Compose**.

**Autor:** Ulises Sánchez Camarena – Desarrollo de bases de datos para web, CUValles (UdeG)

## Arquitectura

```
Navegador ──► http://localhost:80 ──► [ web: Gunicorn + Flask :8000 ] ──► [ db: MySQL 8 :3306 ]
                                                                               │
                                                                        volumen db_data
```

| Servicio | Imagen | Función |
|---|---|---|
| `web` | construida con el `Dockerfile` (python:3.13-slim) | Ejecuta la app con Gunicorn (3 workers) |
| `db` | `mysql:8.0` | Base de datos `videojuegos`; los datos persisten en el volumen `db_data` |

## Estructura del proyecto

```
videojuegos-prod/
├── app/
│   ├── __init__.py      # create_app(): configura Flask, SQLAlchemy, Flask-Login y crea las tablas
│   ├── config.py        # Configs: development, testing y production (lee variables de entorno)
│   ├── models.py        # Modelos Juego y Usuario
│   ├── auth.py          # Registro, login y logout
│   ├── routes.py        # CRUD de juegos (rutas protegidas con @login_required)
│   ├── api/routes.py    # API REST con Flask-RESTful
│   └── templates/       # Plantillas Jinja2 (Bulma)
├── wsgi.py              # Punto de entrada para Gunicorn
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye Docker Compose). En Windows, con WSL 2 activado.
- El puerto 80 libre (si tienes XAMPP, detén Apache).

## Pasos para levantar la aplicación en producción

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/UlisesSC-coder/videojuegos-prod.git
   cd videojuegos-prod
   ```
2. Construir las imágenes y levantar los contenedores en segundo plano:
   ```bash
   docker compose up -d --build
   ```
3. Esperar a que MySQL quede `healthy` (la primera vez tarda ~30 s):
   ```bash
   docker compose ps
   ```
4. Abrir **http://localhost** en el navegador.

Las tablas `juegos` y `usuarios_app` se crean automáticamente al arrancar la aplicación.

## Variables de entorno

| Variable | Servicio | Descripción | Valor usado |
|---|---|---|---|
| `FLASK_ENV` | web | Elige la configuración de `app/config.py` | `production` |
| `DATABASE_URL` | web | Cadena de conexión de SQLAlchemy a MySQL (el host `db` es el nombre del servicio en Compose) | `mysql+pymysql://user:pwd@db/videojuegos` |
| `SECRET_KEY` | web | Firma la cookie de sesión de Flask-Login. Debe ser la misma para todos los workers de Gunicorn | `cambia_esta_clave` |
| `SESSION_COOKIE_SECURE` | web | `True` = la cookie solo viaja por HTTPS. En `http://localhost` debe ser `False` | `False` |
| `MYSQL_ROOT_PASSWORD` | db | Contraseña del usuario root de MySQL | `rootpwd` |
| `MYSQL_DATABASE` | db | Base de datos que se crea al iniciar | `videojuegos` |
| `MYSQL_USER` / `MYSQL_PASSWORD` | db | Usuario de la aplicación | `user` / `pwd` |

> En un despliegue real, `SECRET_KEY` y las contraseñas no se escriben en el `docker-compose.yml`: se guardan en un archivo `.env` (excluido de Git) o en un gestor de secretos.

## Comandos Docker / Docker Compose usados

| Comando | Para qué sirve |
|---|---|
| `docker compose up -d --build` | Construye la imagen de `web` y levanta `db` y `web` en segundo plano |
| `docker compose ps` | Muestra el estado de los contenedores (`db` debe estar `healthy`) |
| `docker compose logs -f web` | Muestra en vivo los logs de Gunicorn (peticiones y errores) |
| `docker compose logs db` | Logs de MySQL |
| `docker compose exec db mysql -uuser -ppwd videojuegos` | Entrar a la consola de MySQL dentro del contenedor |
| `docker compose restart web` | Reiniciar solo la aplicación |
| `docker compose down` | Detener y eliminar los contenedores (los datos se conservan en el volumen) |
| `docker compose down -v` | Detener todo **y borrar** el volumen de la base de datos |

## Decisiones de configuración para producción

- **Gunicorn en lugar del servidor de Flask:** el servidor de `flask run` es solo para desarrollo; Gunicorn atiende varias peticiones a la vez con 3 *workers*.
- **`wsgi.py`:** Gunicorn necesita una variable con la aplicación; como el proyecto usa el patrón *application factory* (`create_app()`), `wsgi.py` la crea.
- **`--preload`:** la app (y la creación de tablas) se ejecuta una sola vez antes de crear los workers, así no compiten tres procesos por crear las mismas tablas.
- **Sesiones con varios workers:** la sesión vive en una cookie firmada con `SECRET_KEY`. Como la clave es fija (viene de una variable de entorno), cualquier worker puede validar la sesión y el usuario no pierde el login.
- **`healthcheck` + `depends_on: condition: service_healthy`:** la app espera a que MySQL acepte conexiones, no solo a que el contenedor esté encendido.
- **`cryptography` en requirements:** MySQL 8 usa la autenticación `caching_sha2_password`, que PyMySQL necesita para conectarse.
- **Python 3.13:** misma versión con la que se desarrolló y probó el proyecto.
- **Usuario sin privilegios (`appuser`)** dentro del contenedor y `.dockerignore` para no copiar el `venv` ni archivos innecesarios a la imagen.


