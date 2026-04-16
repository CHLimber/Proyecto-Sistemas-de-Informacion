from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from ..extensions import db
from ..models.auth import Usuario
from ..bitacora import log

bp = Blueprint('auth', __name__)


@bp.post('/login')
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    max_intentos = current_app.config['LOGIN_MAX_INTENTOS']
    bloqueo_minutos = current_app.config['LOGIN_BLOQUEO_MINUTOS']

    usuario = Usuario.query.filter_by(username=username, estado=True).first()

    if not usuario:
        log('LOGIN_FALLIDO', f"Intento con usuario inexistente '{username}'")
        return jsonify({'error': 'Credenciales inválidas'}), 401

    if usuario.bloqueado_hasta and datetime.now() < usuario.bloqueado_hasta:
        segundos_restantes = int((usuario.bloqueado_hasta - datetime.now()).total_seconds())
        minutos = segundos_restantes // 60
        segundos = segundos_restantes % 60
        log('LOGIN_BLOQUEADO', f"Usuario '{username}' bloqueado — {segundos_restantes}s restantes")
        return jsonify({
            'error': f'Cuenta bloqueada. Intente en {minutos}m {segundos}s.',
            'bloqueado_hasta': usuario.bloqueado_hasta.isoformat(),
        }), 423

    if not check_password_hash(usuario.password, password):
        usuario.intentos_fallidos += 1

        if usuario.intentos_fallidos >= max_intentos:
            usuario.bloqueado_hasta = datetime.now() + timedelta(minutes=bloqueo_minutos)
            db.session.commit()
            log('LOGIN_BLOQUEADO', f"Usuario '{username}' bloqueado tras {max_intentos} intentos fallidos")
            return jsonify({
                'error': f'Cuenta bloqueada por {bloqueo_minutos} minutos tras {max_intentos} intentos fallidos.',
                'bloqueado_hasta': usuario.bloqueado_hasta.isoformat(),
            }), 423

        restantes = max_intentos - usuario.intentos_fallidos
        db.session.commit()
        log('LOGIN_FALLIDO', f"Contraseña incorrecta para '{username}' — intento {usuario.intentos_fallidos}/{max_intentos}")
        return jsonify({'error': f'Credenciales inválidas. Intentos restantes: {restantes}.'}), 401

    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.ultimo_acceso = datetime.now()
    db.session.commit()

    token = create_access_token(identity=str(usuario.id))
    log('LOGIN', f"Usuario '{username}' inició sesión", username)

    return jsonify({
        'access_token': token,
        'usuario': {
            'id': usuario.id,
            'username': usuario.username,
            'rol': usuario.rol.nombre,
        }
    })


@bp.get('/me')
@jwt_required()
def me():
    id_usuario = int(get_jwt_identity())
    usuario = db.get_or_404(Usuario, id_usuario)
    return jsonify({
        'id': usuario.id,
        'username': usuario.username,
        'rol': usuario.rol.nombre,
    })
