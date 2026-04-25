from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..extensions import db
from ..models.orden import OrdenTrabajo, OrdenEmpleado, OrdenProducto, OrdenHistorial, EstadoOrden
from ..models.entidad import Empleado
from ..bitacora import log
from ..permisos import requiere_permiso

bp = Blueprint('ordenes', __name__)


@bp.get('/')
@jwt_required()
@requiere_permiso('ver_ordenes')
def listar():
    ordenes = OrdenTrabajo.query.order_by(OrdenTrabajo.id.desc()).all()
    return jsonify([_serializar(o) for o in ordenes])


@bp.get('/estados')
@jwt_required()
@requiere_permiso('ver_ordenes')
def listar_estados():
    estados = EstadoOrden.query.order_by(EstadoOrden.orden).all()
    return jsonify([{'id': e.id, 'nombre': e.nombre} for e in estados])


@bp.get('/<int:id_orden>')
@jwt_required()
@requiere_permiso('ver_ordenes')
def obtener(id_orden):
    o = db.get_or_404(OrdenTrabajo, id_orden)
    return jsonify(_serializar(o, detalle=True))


@bp.post('/')
@jwt_required()
@requiere_permiso('crear_ordenes')
def crear():
    data = request.get_json()
    id_usuario = int(get_jwt_identity())

    for campo in ['id_proyecto', 'id_servicio', 'id_estado_orden']:
        if not data.get(campo):
            return jsonify({'error': f'El campo {campo} es requerido'}), 400

    prefijo = datetime.now().strftime('OT-%Y%m-')
    ultimo = (OrdenTrabajo.query
              .filter(OrdenTrabajo.codigo.like(f'{prefijo}%'))
              .order_by(OrdenTrabajo.id.desc())
              .first())
    siguiente = 1
    if ultimo:
        try:
            siguiente = int(ultimo.codigo.split('-')[-1]) + 1
        except ValueError:
            pass
    codigo = f"{prefijo}{siguiente:04d}"

    orden = OrdenTrabajo(
        codigo=codigo,
        id_proyecto=data['id_proyecto'],
        id_servicio=data['id_servicio'],
        id_estado_orden=data['id_estado_orden'],
        id_usuario=id_usuario,
        descripcion=data.get('descripcion', '').strip() or None,
        fecha_ejecucion=data.get('fecha_ejecucion') or None,
        tiempo_estimado=data.get('tiempo_estimado') or None,
        observaciones=data.get('observaciones', '').strip() or None,
    )
    db.session.add(orden)
    db.session.flush()

    # Empleados asignados
    for emp in data.get('empleados', []):
        if not emp.get('id_empleado'):
            continue
        oe = OrdenEmpleado(
            id_orden_trabajo=orden.id,
            id_empleado=emp['id_empleado'],
            es_responsable=emp.get('es_responsable', False),
        )
        db.session.add(oe)

    # Productos asignados
    for prod in data.get('productos', []):
        if not prod.get('id_producto') or not prod.get('cantidad_asignada'):
            continue
        op = OrdenProducto(
            id_orden_trabajo=orden.id,
            id_producto=prod['id_producto'],
            cantidad_asignada=prod['cantidad_asignada'],
        )
        db.session.add(op)

    # Historial inicial
    hist = OrdenHistorial(
        id_orden_trabajo=orden.id,
        id_estado_anterior=None,
        id_estado_nuevo=data['id_estado_orden'],
        id_usuario=id_usuario,
        observacion='Orden creada',
    )
    db.session.add(hist)
    db.session.commit()

    log('CREAR_ORDEN', f"Orden {codigo} creada para proyecto {data['id_proyecto']}", str(id_usuario))
    return jsonify(_serializar(orden, detalle=True)), 201


@bp.put('/<int:id_orden>')
@jwt_required()
@requiere_permiso('editar_ordenes')
def actualizar(id_orden):
    o = db.get_or_404(OrdenTrabajo, id_orden)
    data = request.get_json()
    id_usuario = int(get_jwt_identity())

    if 'descripcion' in data:
        o.descripcion = data['descripcion'].strip() or None
    if 'observaciones' in data:
        o.observaciones = data['observaciones'].strip() or None
    if 'fecha_ejecucion' in data:
        o.fecha_ejecucion = data['fecha_ejecucion'] or None
    if 'tiempo_estimado' in data:
        o.tiempo_estimado = data['tiempo_estimado'] or None

    if 'id_estado_orden' in data and data['id_estado_orden'] != o.id_estado_orden:
        estado_anterior = o.id_estado_orden
        o.id_estado_orden = data['id_estado_orden']
        hist = OrdenHistorial(
            id_orden_trabajo=o.id,
            id_estado_anterior=estado_anterior,
            id_estado_nuevo=data['id_estado_orden'],
            id_usuario=id_usuario,
            observacion=data.get('observacion_cambio', ''),
        )
        db.session.add(hist)

    db.session.commit()
    log('ACTUALIZAR_ORDEN', f"Orden {id_orden} actualizada", str(id_usuario))
    return jsonify(_serializar(o, detalle=True))


def _serializar(o: OrdenTrabajo, detalle: bool = False) -> dict:
    data = {
        'id': o.id,
        'codigo': o.codigo,
        'id_proyecto': o.id_proyecto,
        'id_servicio': o.id_servicio,
        'id_estado_orden': o.id_estado_orden,
        'estado_nombre': o.estado.nombre if o.estado else None,
        'descripcion': o.descripcion,
        'fecha_ejecucion': o.fecha_ejecucion.isoformat() if o.fecha_ejecucion else None,
        'tiempo_estimado': o.tiempo_estimado,
        'observaciones': o.observaciones,
        'fecha_creacion': o.fecha_creacion.isoformat() if o.fecha_creacion else None,
    }
    if detalle:
        data['empleados'] = [
            {'id_empleado': e.id_empleado, 'es_responsable': e.es_responsable}
            for e in o.empleados
        ]
        data['productos'] = [
            {
                'id_producto': p.id_producto,
                'cantidad_asignada': float(p.cantidad_asignada),
                'cantidad_usada': float(p.cantidad_usada) if p.cantidad_usada else None,
            }
            for p in o.productos
        ]
        data['historial'] = [
            {
                'id_estado_anterior': h.id_estado_anterior,
                'id_estado_nuevo': h.id_estado_nuevo,
                'fecha_cambio': h.fecha_cambio.isoformat() if h.fecha_cambio else None,
                'observacion': h.observacion,
            }
            for h in o.historial
        ]
    return data
