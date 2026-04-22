# app/models/models.py

from app import db
from datetime import datetime

class Usuario(db.Model):
    """Modelo de Usuario para la base de datos"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M')
        }




    #  Itinerario

class Departamento(db.Model):
    """Modelo para los departamentos del estadio"""
    __tablename__ = 'departamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    color = db.Column(db.String(7), default='#007bff')  # Color para identificar
    
    # Relación con eventos
    eventos = db.relationship('Evento', backref='departamento', lazy=True)
    
    def __repr__(self):
        return f'<Departamento {self.nombre}>'

class Evento(db.Model):
    """Modelo para los eventos del itinerario"""
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500))
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    duracion_minutos = db.Column(db.Integer, default=30)
    
    # Llave foránea al departamento
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=False)
    
    # Estado del evento
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, en_curso, completado, cancelado
    
    # Guión a ejecutar
    guion = db.Column(db.Text)  # Instrucciones detalladas
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Evento {self.titulo}>'

class Sincronizacion(db.Model):
    """Modelo para sincronizar eventos entre departamentos"""
    __tablename__ = 'sincronizaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    
    # Fecha y hora de sincronización
    fecha_sincronizacion = db.Column(db.Date, nullable=False)
    hora_sincronizacion = db.Column(db.Time, nullable=False)
    
    # Estado de la sincronización
    estado = db.Column(db.String(20), default='programada')  # programada, ejecutada, cancelada
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con eventos sincronizados
    eventos = db.relationship('EventoSincronizado', backref='sincronizacion', lazy=True)

class EventoSincronizado(db.Model):
    """Modelo para eventos que se ejecutan sincronizados"""
    __tablename__ = 'eventos_sincronizados'
    
    id = db.Column(db.Integer, primary_key=True)
    sincronizacion_id = db.Column(db.Integer, db.ForeignKey('sincronizaciones.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    orden = db.Column(db.Integer, default=0)  # Orden de ejecución
    ejecutado = db.Column(db.Boolean, default=False)
    ejecutado_en = db.Column(db.DateTime)
    
    evento = db.relationship('Evento', backref='sincronizaciones')