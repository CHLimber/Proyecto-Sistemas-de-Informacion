import os
from flask import Flask, send_from_directory
from .config import config
from .extensions import db, migrate, jwt, cors, mail


def create_app(env: str = None):
    app = Flask(__name__)
    env = env or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[env])

    DIST_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'frontend', 'dist'
    )

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r'/api/*': {'origins': '*'}})
    mail.init_app(app)

    # Blueprints
    from .routes.auth import bp as auth_bp
    from .routes.entidades import bp as entidades_bp
    from .routes.cotizaciones import bp as cotizaciones_bp
    from .routes.proyectos import bp as proyectos_bp
    from .routes.ordenes import bp as ordenes_bp
    from .routes.mantenimiento import bp as mantenimiento_bp
    from .routes.finanzas import bp as finanzas_bp
    from .routes.notificaciones import bp as notificaciones_bp
    from .routes.catalogos import bp as catalogos_bp
    from .routes.productos import bp as productos_bp
    from .routes.usuarios import bp as usuarios_bp

    app.register_blueprint(auth_bp,          url_prefix='/api/auth')
    app.register_blueprint(entidades_bp,     url_prefix='/api/entidades')
    app.register_blueprint(cotizaciones_bp,  url_prefix='/api/cotizaciones')
    app.register_blueprint(proyectos_bp,     url_prefix='/api/proyectos')
    app.register_blueprint(ordenes_bp,       url_prefix='/api/ordenes')
    app.register_blueprint(mantenimiento_bp, url_prefix='/api/mantenimiento')
    app.register_blueprint(finanzas_bp,      url_prefix='/api/finanzas')
    app.register_blueprint(notificaciones_bp,url_prefix='/api/notificaciones')
    app.register_blueprint(catalogos_bp,     url_prefix='/api/catalogos')
    app.register_blueprint(productos_bp,     url_prefix='/api/productos')
    app.register_blueprint(usuarios_bp,      url_prefix='/api/usuarios')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path):
        if path and os.path.exists(os.path.join(DIST_DIR, path)):
            return send_from_directory(DIST_DIR, path)
        return send_from_directory(DIST_DIR, 'index.html')

    return app
