from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.producto import Producto
from ..models.catalogo import Categoria
from ..bitacora import log

bp = Blueprint('productos', __name__)


@bp.get('/')
@jwt_required()
def listar():
    productos = Producto.query.filter_by(estado=True).order_by(Producto.nombre).all()
    return jsonify([_serializar(p) for p in productos])


@bp.get('/<int:id_producto>')
@jwt_required()
def obtener(id_producto):
    p = db.get_or_404(Producto, id_producto)
    return jsonify(_serializar(p))


@bp.post('/')
@jwt_required()
def crear():
    data = request.get_json()
    usuario = get_jwt_identity()

    campos_requeridos = ['codigo', 'nombre', 'unidad_medida', 'id_categoria']
    for campo in campos_requeridos:
        if not data.get(campo):
            return jsonify({'error': f'El campo {campo} es requerido'}), 400

    if Producto.query.filter_by(codigo=data['codigo']).first():
        return jsonify({'error': 'Ya existe un producto con ese código'}), 409

    if not Categoria.query.filter_by(id=data['id_categoria'], estado=True).first():
        return jsonify({'error': 'Categoría no válida'}), 400

    producto = Producto(
        codigo=data['codigo'].strip().upper(),
        nombre=data['nombre'].strip(),
        unidad_medida=data['unidad_medida'].strip(),
        id_categoria=data['id_categoria'],
        descripcion=data.get('descripcion', '').strip() or None,
    )
    db.session.add(producto)
    db.session.commit()
    log('CREAR_PRODUCTO', f"Producto '{producto.nombre}' (cod: {producto.codigo}) creado", usuario)
    return jsonify(_serializar(producto)), 201


@bp.put('/<int:id_producto>')
@jwt_required()
def actualizar(id_producto):
    p = db.get_or_404(Producto, id_producto)
    data = request.get_json()
    usuario = get_jwt_identity()

    if 'codigo' in data:
        codigo_nuevo = data['codigo'].strip().upper()
        existente = Producto.query.filter_by(codigo=codigo_nuevo).first()
        if existente and existente.id != id_producto:
            return jsonify({'error': 'Ya existe un producto con ese código'}), 409
        p.codigo = codigo_nuevo

    if 'nombre' in data:
        p.nombre = data['nombre'].strip()
    if 'unidad_medida' in data:
        p.unidad_medida = data['unidad_medida'].strip()
    if 'descripcion' in data:
        p.descripcion = data['descripcion'].strip() or None
    if 'id_categoria' in data:
        if not Categoria.query.filter_by(id=data['id_categoria'], estado=True).first():
            return jsonify({'error': 'Categoría no válida'}), 400
        p.id_categoria = data['id_categoria']

    db.session.commit()
    log('ACTUALIZAR_PRODUCTO', f"Producto {id_producto} actualizado", usuario)
    return jsonify(_serializar(p))


@bp.delete('/<int:id_producto>')
@jwt_required()
def desactivar(id_producto):
    p = db.get_or_404(Producto, id_producto)
    p.estado = False
    db.session.commit()
    usuario = get_jwt_identity()
    log('DESACTIVAR_PRODUCTO', f"Producto {id_producto} desactivado", usuario)
    return jsonify({'mensaje': 'Producto desactivado'})


def _serializar(p: Producto) -> dict:
    return {
        'id': p.id,
        'codigo': p.codigo,
        'nombre': p.nombre,
        'unidad_medida': p.unidad_medida,
        'descripcion': p.descripcion,
        'id_categoria': p.id_categoria,
        'estado': p.estado,
    }
