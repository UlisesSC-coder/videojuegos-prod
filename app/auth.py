from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from . import db
from .models import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Usuario y contraseña son obligatorios.", "danger")
        elif Usuario.query.filter_by(username=username).first():
            flash("Ese usuario ya existe.", "danger")
        else:
            usuario = Usuario(username=username)
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            flash("Cuenta creada, ahora inicia sesión.", "success")
            return redirect(url_for("auth.login"))

    return render_template("registro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        usuario = Usuario.query.filter_by(username=username).first()

        if usuario is None or not usuario.check_password(password):
            flash("Usuario o contraseña incorrectos.", "danger")
        else:
            login_user(usuario)
            siguiente = request.args.get("next")
            if not siguiente or not siguiente.startswith("/") or siguiente.startswith("//"):
                siguiente = url_for("main.juegos")
            return redirect(siguiente)

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("main.juegos"))