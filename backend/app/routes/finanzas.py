from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal
from ..extensions import db
from ..models.finanzas import Pago, GastoOrden
from ..bitacora import log
from ..permisos import requiere_permiso

bp = Blueprint('finanzas', __name__)

TIPOS_PAGO   = ('anticipo', 'pago_parcial', 'pago_final', 'otro')
METODOS_PAGO = ('efectivo', 'transferencia', 'QR', 'otro')
CONCEPTOS    = ('materiales', 'viaticos', 'transporte', 'otro')


# ── PAGOS ────────────────────────────────────────────────────────

@bp.get('/pagos')
@jwt_required()
@requiere_permiso('ver_finanzas')
def listar_pagos():
    pagos = Pago.query.order_by(Pago.fecha_pago.desc()).all()
    return jsonify([_serializar_pago(p) for p in pagos])


@bp.get('/pagos/proyecto/<int:id_proyecto>')
@jwt_required()
@requiere_permiso('ver_finanzas')
def pagos_por_proyecto(id_proyecto):
    pagos = Pago.query.filter_by(id_proyecto=id_proyecto).order_by(Pago.fecha_pago.desc()).all()
    total = sum(p.monto for p in pagos)
    return jsonify({'pagos': [_serializar_pago(p) for p in pagos], 'total_pagado': float(total)})


@bp.post('/pagos')
@jwt_required()
@requiere_permiso('gestionar_finanzas')
def registrar_pago():
    data = request.get_json()
    id_usuario = int(get_jwt_identity())

    for campo in ['id_proyecto', 'tipo_pago', 'monto', 'fecha_pago', 'metodo']:
        if not data.get(campo):
            return jsonify({'error': f'El campo {campo} es requerido'}), 400

    if data['tipo_pago'] not in TIPOS_PAGO:
        return jsonify({'error': f'Tipo de pago inválido'}), 400
    if data['metodo'] not in METODOS_PAGO:
        return jsonify({'error': f'Método de pago inválido'}), 400

    try:
        monto = Decimal(str(data['monto']))
        if monto <= 0:
            raise ValueError
    except (ValueError, Exception):
        return jsonify({'error': 'El monto debe ser un número positivo'}), 400

    pago = Pago(
        id_proyecto=data['id_proyecto'],
        id_usuario=id_usuario,
        tipo_pago=data['tipo_pago'],
        monto=monto,
        fecha_pago=data['fecha_pago'],
        metodo=data['metodo'],
        observacion=data.get('observacion', '').strip() or None,
    )
    db.session.add(pago)
    db.session.commit()
    log('REGISTRAR_PAGO', f"Pago {data['tipo_pago']} de Bs {monto} registrado para proyecto {data['id_proyecto']}",
        id_usuario=id_usuario, modulo='finanzas')
    return jsonify(_serializar_pago(pago)), 201


# ── GASTOS ───────────────────────────────────────────────────────

@bp.get('/gastos')
@jwt_required()
@requiere_permiso('ver_finanzas')
def listar_gastos():
    gastos = GastoOrden.query.order_by(GastoOrden.fecha_gasto.desc()).all()
    return jsonify([_serializar_gasto(g) for g in gastos])


@bp.post('/gastos')
@jwt_required()
@requiere_permiso('gestionar_finanzas')
def registrar_gasto():
    data = request.get_json()
    id_usuario = int(get_jwt_identity())

    for campo in ['id_orden', 'concepto', 'monto', 'fecha_gasto']:
        if not data.get(campo):
            return jsonify({'error': f'El campo {campo} es requerido'}), 400

    if data['concepto'] not in CONCEPTOS:
        return jsonify({'error': 'Concepto inválido'}), 400

    try:
        monto = Decimal(str(data['monto']))
        if monto <= 0:
            raise ValueError
    except Exception:
        return jsonify({'error': 'El monto debe ser un número positivo'}), 400

    gasto = GastoOrden(
        id_orden=data['id_orden'],
        id_usuario=id_usuario,
        concepto=data['concepto'],
        descripcion=data.get('descripcion', '').strip() or None,
        monto=monto,
        fecha_gasto=data['fecha_gasto'],
    )
    db.session.add(gasto)
    db.session.commit()
    log('REGISTRAR_GASTO', f"Gasto '{data['concepto']}' de Bs {monto} en orden {data['id_orden']}",
        id_usuario=id_usuario, modulo='finanzas')
    return jsonify(_serializar_gasto(gasto)), 201


# ── VISTA: cuentas por cobrar ─────────────────────────────────────

@bp.get('/cuentas-por-cobrar')
@jwt_required()
@requiere_permiso('ver_finanzas')
def cuentas_por_cobrar():
    from ..extensions import db
    from sqlalchemy import text
    resultado = db.session.execute(text('SELECT * FROM cuentas_por_cobrar')).fetchall()
    return jsonify([{
        'id_proyecto': r.id_proyecto,
        'codigo_proyecto': r.codigo_proyecto,
        'cliente': r.cliente,
        'monto_total_cotizacion': float(r.monto_total_cotizacion),
        'total_pagado': float(r.total_pagado),
        'saldo_pendiente': float(r.saldo_pendiente),
    } for r in resultado])


def _serializar_pago(p: Pago) -> dict:
    return {
        'id': p.id,
        'id_proyecto': p.id_proyecto,
        'tipo_pago': p.tipo_pago,
        'metodo': p.metodo,
        'monto': float(p.monto),
        'fecha_pago': p.fecha_pago.isoformat() if p.fecha_pago else None,
        'observacion': p.observacion,
        'fecha_registro': p.fecha_registro.isoformat() if p.fecha_registro else None,
    }


def _serializar_gasto(g: GastoOrden) -> dict:
    return {
        'id': g.id,
        'id_orden': g.id_orden,
        'concepto': g.concepto,
        'descripcion': g.descripcion,
        'monto': float(g.monto),
        'fecha_gasto': g.fecha_gasto.isoformat() if g.fecha_gasto else None,
        'fecha_registro': g.fecha_registro.isoformat() if g.fecha_registro else None,
    }
