# app/models/guion_model.py

from app import db
from datetime import datetime
import hashlib

class Guion(db.Model):
    """Modelo para gestión de guiones del estadio"""
    __tablename__ = 'guiones'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    
    # Datos del evento
    fecha_evento = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    tiempo_estimado = db.Column(db.Integer, default=30)
    
    # Tipo de evento
    tipo_evento = db.Column(db.String(50), default='regular')
    
    # Contenido del guión
    salida = db.Column(db.Text)  # Lo que se muestra en pantalla
    instrucciones = db.Column(db.Text)  # Instrucciones para trabajadores
    
    # Estado
    estado = db.Column(db.String(20), default='borrador')
    
    # Control de duplicados
    hash_unico = db.Column(db.String(64), unique=True)
    
    # Auditoría
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    publicado_en = db.Column(db.DateTime)
    modificado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Guion {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha_evento': self.fecha_evento.strftime('%Y-%m-%d') if self.fecha_evento else None,
            'hora_inicio': self.hora_inicio.strftime('%H:%M') if self.hora_inicio else None,
            'hora_fin': self.hora_fin.strftime('%H:%M') if self.hora_fin else None,
            'tiempo_estimado': self.tiempo_estimado,
            'tipo_evento': self.tipo_evento,
            'salida': self.salida,
            'instrucciones': self.instrucciones,
            'estado': self.estado
        }
    
    @staticmethod
    def generar_hash(titulo, fecha_evento):
        """Generar hash único para evitar duplicados"""
        contenido = f"{titulo}|{fecha_evento}"
        return hashlib.sha256(contenido.encode()).hexdigest()