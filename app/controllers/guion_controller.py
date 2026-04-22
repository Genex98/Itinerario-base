# app/controllers/guion_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from app import db
from app.models.guion_model import Guion
from app.forms.guion_form import GuionForm, PublicarGuionForm

# Crear el Blueprint
bp = Blueprint('guion', __name__, url_prefix='/guiones')


@bp.route('/login')
def login_page():
    """Página de login"""
    return render_template('login.html')

@bp.route('/')
def dashboard():
    """Dashboard principal - Lista de guiones"""
    guiones = Guion.query.order_by(Guion.fecha_evento.desc(), Guion.hora_inicio).all()
    
    total = Guion.query.count()
    borradores = Guion.query.filter_by(estado='borrador').count()
    publicados = Guion.query.filter_by(estado='publicado').count()
    
    return render_template('guion/dashboard.html',
                         guiones=guiones,
                         total=total,
                         borradores=borradores,
                         publicados=publicados)

@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    """Crear un nuevo guión"""
    form = GuionForm()
    
    if form.validate_on_submit():
        # Verificar duplicado
        hash_unico = Guion.generar_hash(form.titulo.data, form.fecha_evento.data)
        existente = Guion.query.filter_by(hash_unico=hash_unico).first()
        
        if existente:
            flash('⚠️ Ya existe un guión con el mismo título y fecha', 'warning')
            return redirect(url_for('guion.crear'))
        
        nuevo_guion = Guion(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            fecha_evento=form.fecha_evento.data,
            hora_inicio=form.hora_inicio.data,
            hora_fin=form.hora_fin.data,
            tiempo_estimado=form.tiempo_estimado.data,
            tipo_evento=form.tipo_evento.data,
            salida=form.salida.data,
            instrucciones=form.instrucciones.data,
            hash_unico=hash_unico,
            estado='borrador'
        )
        
        db.session.add(nuevo_guion)
        db.session.commit()
        
        flash('✅ ¡Guión creado exitosamente!', 'success')
        return redirect(url_for('guion.dashboard'))
    
    return render_template('guion/crear.html', form=form)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Editar un guión existente"""
    guion = Guion.query.get_or_404(id)
    form = GuionForm(obj=guion)
    
    if form.validate_on_submit():
        guion.titulo = form.titulo.data
        guion.descripcion = form.descripcion.data
        guion.fecha_evento = form.fecha_evento.data
        guion.hora_inicio = form.hora_inicio.data
        guion.hora_fin = form.hora_fin.data
        guion.tiempo_estimado = form.tiempo_estimado.data
        guion.tipo_evento = form.tipo_evento.data
        guion.salida = form.salida.data
        guion.instrucciones = form.instrucciones.data
        guion.modificado_en = datetime.utcnow()
        
        db.session.commit()
        flash('✅ ¡Guión actualizado!', 'success')
        return redirect(url_for('guion.dashboard'))
    
    return render_template('guion/editar.html', form=form, guion=guion)

@bp.route('/previsualizar/<int:id>')
def previsualizar(id):
    """Vista previa del guión"""
    guion = Guion.query.get_or_404(id)
    return render_template('guion/previsualizar.html', guion=guion)

@bp.route('/publicar/<int:id>', methods=['GET', 'POST'])
def publicar(id):
    """Publicar un guión"""
    guion = Guion.query.get_or_404(id)
    form = PublicarGuionForm()
    
    if form.validate_on_submit():
        guion.estado = 'publicado'
        guion.publicado_en = datetime.utcnow()
        db.session.commit()
        flash(f'✅ Guión "{guion.titulo}" publicado!', 'success')
        return redirect(url_for('guion.dashboard'))
    
    return render_template('guion/publicar.html', form=form, guion=guion)

@bp.route('/eliminar/<int:id>')
def eliminar(id):
    """Eliminar un guión"""
    guion = Guion.query.get_or_404(id)
    titulo = guion.titulo
    db.session.delete(guion)
    db.session.commit()
    flash(f'🗑️ Guión "{titulo}" eliminado', 'warning')
    return redirect(url_for('guion.dashboard'))

@bp.route('/api/verificar-duplicado', methods=['POST'])
def verificar_duplicado():
    """API para verificar si un guión ya existe"""
    data = request.get_json()
    titulo = data.get('titulo')
    fecha = data.get('fecha')
    
    if titulo and fecha:
        hash_unico = Guion.generar_hash(titulo, fecha)
        existe = Guion.query.filter_by(hash_unico=hash_unico).first()
        return jsonify({'existe': existe is not None})
    
    return jsonify({'existe': False})