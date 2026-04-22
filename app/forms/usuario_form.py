# app/forms/usuario_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

class UsuarioForm(FlaskForm):
    """Formulario para crear/editar usuarios"""
    
    nombre = StringField('Nombre', 
                        validators=[DataRequired(message='El nombre es obligatorio'),
                                   Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')])
    
    email = EmailField('Correo Electrónico',
                      validators=[DataRequired(message='El email es obligatorio'),
                                 Email(message='Ingrese un email válido')])
    
    telefono = StringField('Teléfono',
                          validators=[Optional(),
                                     Length(max=20, message='Máximo 20 caracteres')])
    
    submit = SubmitField('Guardar')