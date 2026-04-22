# app/controllers/usuario_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.models import Usuario
from app import db
from app.forms.usuario_form import UsuarioForm

bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

@bp.route('/')
def dashboard():
    """Dashboard principal"""
    usuarios = Usuario.query.all()
    form = UsuarioForm()  # ← Crear el formulario
    return render_template('usuario/dashboard.html', 
                         usuarios=usuarios,
                         form=form)  # ← Pasar el formulario a la plantilla

@bp.route('/crear', methods=['POST'])
def crear():
    """Crear usuario"""
    form = UsuarioForm()
    
    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            telefono=form.telefono.data
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('¡Usuario creado exitosamente!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')
    
    return redirect(url_for('usuario.dashboard'))

@bp.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    """Editar usuario"""
    usuario = Usuario.query.get_or_404(id)
    form = UsuarioForm()
    
    if form.validate_on_submit():
        usuario.nombre = form.nombre.data
        usuario.email = form.email.data
        usuario.telefono = form.telefono.data
        db.session.commit()
        flash('¡Usuario actualizado exitosamente!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')
    
    return redirect(url_for('usuario.dashboard'))

@bp.route('/eliminar/<int:id>')
def eliminar(id):
    """Eliminar usuario"""
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado correctamente', 'warning')
    return redirect(url_for('usuario.dashboard'))