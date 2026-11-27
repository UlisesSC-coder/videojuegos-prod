from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import db
from .models import Juego

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/juegos")
def juegos():
    juegos = Juego.query.order_by(Juego.id).all()
    return render_template("juegos.html", juegos=juegos)


@main_bp.route("/agregar_juego")
@login_required
def formulario_agregar_juego():
    return render_template("agregar_juego.html")


@main_bp.route("/guardar_juego", methods=["POST"])
@login_required
def guardar_juego():
    juego = Juego(
        nombre=request.form["nombre"],
        descripcion=request.form["descripcion"],
        precio=float(request.form["precio"]),
    )
    db.session.add(juego)
    db.session.commit()
    flash("Juego agregado.", "success")
    return redirect(url_for("main.juegos"))


@main_bp.route("/eliminar_juego", methods=["POST"])
@login_required
def eliminar_juego():
    juego = db.get_or_404(Juego, int(request.form["id"]))
    db.session.delete(juego)
    db.session.commit()
    flash("Juego eliminado.", "success")
    return redirect(url_for("main.juegos"))


@main_bp.route("/formulario_editar_juego/<int:id>")
@login_required
def editar_juego(id):
    juego = db.get_or_404(Juego, id)
    return render_template("editar_juego.html", juego=juego)


@main_bp.route("/actualizar_juego", methods=["POST"])
@login_required
def actualizar_juego():
    juego = db.get_or_404(Juego, int(request.form["id"]))
    juego.nombre = request.form["nombre"]
    juego.descripcion = request.form["descripcion"]
    juego.precio = float(request.form["precio"])
    db.session.commit()
    flash("Juego actualizado.", "success")
    return redirect(url_for("main.juegos"))


@main_bp.route("/profile")
@login_required
def profile():
    return render_template("perfil.html", usuario=current_user)