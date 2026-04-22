# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    # Configuraciones
    app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui-cambiala'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estadio.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    csrf.init_app(app)
    
    # Registrar Blueprints
    from app.controllers import dashboard_controller
    app.register_blueprint(dashboard_controller.bp)
    
    from app.controllers import guion_controller
    app.register_blueprint(guion_controller.bp)
    
    from app.controllers import usuario_controller
    app.register_blueprint(usuario_controller.bp)
    
    # Crear las tablas de la base de datos
    with app.app_context():
        db.create_all()    
    return app

