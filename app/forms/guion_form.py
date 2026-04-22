# app/forms/guion_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models.guion_model import Guion

class GuionForm(FlaskForm):
    """Formulario para crear/editar guiones"""
    
    titulo = StringField('Título del Guión', 
                        validators=[DataRequired(message='El título es obligatorio'),
                                   Length(min=3, max=200)])
    
    descripcion = TextAreaField('Descripción', 
                               validators=[Length(max=500)])
    
    fecha_evento = DateField('Fecha del Evento', 
                            validators=[DataRequired(message='La fecha es obligatoria')],
                            format='%Y-%m-%d')
    
    hora_inicio = TimeField('Hora de Inicio', 
                           validators=[DataRequired()],
                           format='%H:%M')
    
    hora_fin = TimeField('Hora de Fin', 
                        validators=[DataRequired()],
                        format='%H:%M')
    
    tiempo_estimado = IntegerField('Tiempo Estimado (minutos)', 
                                   default=30,
                                   validators=[DataRequired()])
    
    tipo_evento = SelectField('Tipo de Evento', choices=[
        ('regular', 'Regular'),
        ('especial', 'Especial'),
        ('emergencia', 'Emergencia'),
        ('mantenimiento', 'Mantenimiento')
    ], validators=[DataRequired()])
    
    salida = TextAreaField('Contenido en Pantalla (Salida)', 
                          description='Texto que se mostrará al público')
    
    instrucciones = TextAreaField('Instrucciones para Trabajadores', 
                                 description='Guión detallado para el personal')
    
    submit = SubmitField('Guardar Guión')


class PublicarGuionForm(FlaskForm):
    """Formulario para publicar guión"""
    submit = SubmitField('Publicar Guión')