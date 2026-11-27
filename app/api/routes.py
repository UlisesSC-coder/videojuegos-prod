from flask import Blueprint, request
from flask_restful import Api, Resource, abort, fields, marshal_with

from .. import db
from ..models import Juego

# --- Blueprint y Api ---
api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# --- Serialización: cómo se ve un Juego en JSON ---
juego_fields = {
    "id": fields.Integer,
    "nombre": fields.String,
    "descripcion": fields.String,
    "precio": fields.Float,
}


def obtener_o_404(id):
    juego = db.session.get(Juego, id)
    if juego is None:
        abort(404, message=f"El juego con id {id} no existe")
    return juego


def validar_juego(data):
    if not isinstance(data, dict):
        abort(400, message="El cuerpo debe ser un JSON válido")

    nombre = data.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip():
        abort(400, message="'nombre' es obligatorio y debe ser texto")

    precio = data.get("precio")
    if isinstance(precio, bool) or not isinstance(precio, (int, float)) or precio < 0:
        abort(400, message="'precio' es obligatorio y debe ser un número >= 0")

    descripcion = data.get("descripcion", "")
    if not isinstance(descripcion, str):
        abort(400, message="'descripcion' debe ser texto")

    return nombre.strip(), descripcion, precio


# --- Recurso 1: la colección ---
class JuegoList(Resource):
    @marshal_with(juego_fields)
    def get(self):
        return Juego.query.order_by(Juego.id).all()

    @marshal_with(juego_fields)
    def post(self):
        nombre, descripcion, precio = validar_juego(request.get_json(silent=True))
        juego = Juego(nombre=nombre, descripcion=descripcion, precio=precio)
        db.session.add(juego)
        db.session.commit()
        return juego, 201


# --- Recurso 2: un juego en particular ---
class JuegoResource(Resource):
    @marshal_with(juego_fields)
    def get(self, id):
        return obtener_o_404(id)

    @marshal_with(juego_fields)
    def put(self, id):
        juego = obtener_o_404(id)
        juego.nombre, juego.descripcion, juego.precio = validar_juego(
            request.get_json(silent=True)
        )
        db.session.commit()
        return juego

    def delete(self, id):
        juego = obtener_o_404(id)
        db.session.delete(juego)
        db.session.commit()
        return "", 204


# --- Rutas ---
api.add_resource(JuegoList, "/juegos")
api.add_resource(JuegoResource, "/juegos/<int:id>")