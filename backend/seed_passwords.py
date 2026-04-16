"""
Ejecutar UNA VEZ para:
1. Agregar columnas intentos_fallidos y bloqueado_hasta a la tabla usuario
2. Actualizar los hashes de contraseña al formato werkzeug (pbkdf2:sha256)

Uso:
    cd backend
    python seed_passwords.py

Credenciales que quedan:
    admin.mendoza   / Admin123!      (Administrador)
    marco.ibanez    / Tecnico123!    (Técnico Superior)
    luis.mamani     / Tecnico123!    (Técnico Superior)
    ana.quispe      / Atencion123!   (Atención al Cliente)
    patricia.medina / Atencion123!   (Atención al Cliente)
    roberto.flores  / Campo123!      (Técnico de Campo)
    miguel.torrez   / Campo123!      (Técnico de Campo)
    diego.rojas     / Campo123!      (Técnico de Campo)
    fernando.chavez / Campo123!      (Técnico de Campo)
    sergio.pedraza  / Campo123!      (Técnico de Campo)
"""

from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db

PASSWORDS = {
    'admin.mendoza':   'Admin123!',
    'marco.ibanez':    'Tecnico123!',
    'luis.mamani':     'Tecnico123!',
    'ana.quispe':      'Atencion123!',
    'patricia.medina': 'Atencion123!',
    'roberto.flores':  'Campo123!',
    'miguel.torrez':   'Campo123!',
    'diego.rojas':     'Campo123!',
    'fernando.chavez': 'Campo123!',
    'sergio.pedraza':  'Campo123!',
}

app = create_app()

with app.app_context():
    from app.models.auth import Usuario
    actualizados = 0
    for username, password in PASSWORDS.items():
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario:
            usuario.password = generate_password_hash(password)
            actualizados += 1
            print(f'  ✓ {username}')
        else:
            print(f'  ✗ {username} — no encontrado en BD')
    db.session.commit()
    print(f'\n{actualizados} usuarios actualizados.')
