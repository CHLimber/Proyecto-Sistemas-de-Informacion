"""
Verifica que @requiere_permiso devuelve 200/403 según el rol del usuario.
No prueba la lógica de negocio de cada endpoint, solo el control de acceso.
"""
from tests.conftest import crear_usuario, login, auth_headers


def _token(client, username, permisos, password='pass1234'):
    crear_usuario(username, permisos, password)
    _, data = login(client, username, password)
    return data['access_token']


# ── gestionar_usuarios ───────────────────────────────────────────────

class TestGestionarUsuarios:
    def test_con_permiso_puede_listar(self, client, app):
        with app.app_context():
            token = _token(client, 'admin_u', ['gestionar_usuarios'])

        rv = client.get('/api/usuarios/', headers=auth_headers(token))
        assert rv.status_code == 200

    def test_sin_permiso_es_403(self, client, app):
        with app.app_context():
            token = _token(client, 'tecnico_u', ['ver_ordenes'])

        rv = client.get('/api/usuarios/', headers=auth_headers(token))
        assert rv.status_code == 403

    def test_sin_jwt_es_401(self, client):
        rv = client.get('/api/usuarios/')
        assert rv.status_code == 401


# ── gestionar_catalogo (productos) ──────────────────────────────────

class TestGestionarCatalogo:
    def test_con_permiso_puede_listar_productos(self, client, app):
        with app.app_context():
            token = _token(client, 'cat_admin', ['gestionar_catalogo'])

        rv = client.get('/api/productos/', headers=auth_headers(token))
        assert rv.status_code == 200

    def test_sin_permiso_no_puede_crear_producto(self, client, app):
        with app.app_context():
            token = _token(client, 'cat_tecnico', ['ver_ordenes'])

        rv = client.post('/api/productos/', json={
            'codigo': 'X001', 'nombre': 'Sensor', 'unidad_medida': 'un', 'id_categoria': 1
        }, headers=auth_headers(token))
        assert rv.status_code == 403


# ── ver_clientes / crear_clientes / editar_clientes ─────────────────

class TestPermisosClientes:
    def test_ver_clientes_con_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'atencion', ['ver_clientes'])

        rv = client.get('/api/entidades/', headers=auth_headers(token))
        assert rv.status_code == 200

    def test_ver_clientes_sin_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'tecnico_campo', ['ver_ordenes', 'ver_mantenimientos'])

        rv = client.get('/api/entidades/', headers=auth_headers(token))
        assert rv.status_code == 403

    def test_crear_cliente_sin_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'solo_ver', ['ver_clientes'])

        rv = client.post('/api/entidades/', json={
            'tipo': 'natural', 'nombre': 'Test', 'ci': '12345678'
        }, headers=auth_headers(token))
        assert rv.status_code == 403


# ── ver_proyectos / crear_proyectos / editar_proyectos ──────────────

class TestPermisosProyectos:
    def test_ver_proyectos_con_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'proy_viewer', ['ver_proyectos'])

        rv = client.get('/api/proyectos/', headers=auth_headers(token))
        assert rv.status_code == 200

    def test_ver_proyectos_sin_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'sin_proy', ['ver_ordenes'])

        rv = client.get('/api/proyectos/', headers=auth_headers(token))
        assert rv.status_code == 403

    def test_crear_proyecto_requiere_permiso_especifico(self, client, app):
        with app.app_context():
            token = _token(client, 'solo_ver_proy', ['ver_proyectos'])

        rv = client.post('/api/proyectos/', json={}, headers=auth_headers(token))
        # Sin crear_proyectos → 403 (no 400, que sería error de validación)
        assert rv.status_code == 403


# ── ver_ordenes / crear_ordenes / editar_ordenes ────────────────────

class TestPermisosOrdenes:
    def test_ver_ordenes_con_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'ord_viewer', ['ver_ordenes'])

        rv = client.get('/api/ordenes/', headers=auth_headers(token))
        assert rv.status_code == 200

    def test_editar_orden_sin_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'ord_readonly', ['ver_ordenes'])

        rv = client.put('/api/ordenes/1', json={}, headers=auth_headers(token))
        assert rv.status_code == 403

    def test_crear_orden_requiere_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'ord_viewer2', ['ver_ordenes'])

        rv = client.post('/api/ordenes/', json={}, headers=auth_headers(token))
        assert rv.status_code == 403


# ── finanzas ─────────────────────────────────────────────────────────

class TestPermisosFinanzas:
    def test_ver_finanzas_con_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'fin_viewer', ['ver_finanzas'])

        rv = client.get('/api/finanzas/pagos', headers=auth_headers(token))
        assert rv.status_code == 200

    def test_registrar_pago_sin_gestionar_finanzas(self, client, app):
        with app.app_context():
            token = _token(client, 'fin_readonly', ['ver_finanzas'])

        rv = client.post('/api/finanzas/pagos', json={}, headers=auth_headers(token))
        assert rv.status_code == 403

    def test_ver_finanzas_sin_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'no_fin', ['ver_ordenes'])

        rv = client.get('/api/finanzas/pagos', headers=auth_headers(token))
        assert rv.status_code == 403


# ── mantenimiento ────────────────────────────────────────────────────

class TestPermisosMantenimiento:
    def test_ver_mantenimientos_con_permiso(self, client, app):
        with app.app_context():
            token = _token(client, 'mant_viewer', ['ver_mantenimientos'])

        rv = client.get('/api/mantenimiento/', headers=auth_headers(token))
        assert rv.status_code == 200

    def test_crear_mantenimiento_requiere_gestionar(self, client, app):
        with app.app_context():
            token = _token(client, 'mant_readonly', ['ver_mantenimientos'])

        rv = client.post('/api/mantenimiento/', json={}, headers=auth_headers(token))
        assert rv.status_code == 403


# ── usuario con múltiples permisos ───────────────────────────────────

class TestMultiplesPermisos:
    def test_tecnico_superior_accede_a_lo_suyo(self, client, app):
        permisos = ['ver_proyectos', 'ver_ordenes', 'ver_clientes',
                    'crear_ordenes', 'editar_ordenes', 'ver_mantenimientos']
        with app.app_context():
            token = _token(client, 'tecnico_sup', permisos)

        assert client.get('/api/proyectos/', headers=auth_headers(token)).status_code == 200
        assert client.get('/api/ordenes/', headers=auth_headers(token)).status_code == 200
        assert client.get('/api/entidades/', headers=auth_headers(token)).status_code == 200

    def test_tecnico_superior_no_puede_gestionar_usuarios(self, client, app):
        permisos = ['ver_proyectos', 'ver_ordenes', 'ver_clientes']
        with app.app_context():
            token = _token(client, 'tecnico_sup2', permisos)

        rv = client.get('/api/usuarios/', headers=auth_headers(token))
        assert rv.status_code == 403
