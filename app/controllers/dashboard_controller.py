# app/controllers/dashboard_controller.py

from flask import Blueprint, render_template
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route('/')
def index():
    """Panel principal"""
    
    # Datos de usuarios en línea
    usuarios_en_linea = {
        'total': 10,
        'departamentos': [
            {'nombre': 'Medios', 'cantidad': 5, 'color': 'primary'},
            {'nombre': 'Palco de Operaciones', 'cantidad': 5, 'color': 'success'}
        ]
    }
    
    # Guión actual
    guion_actual = {
        'estado': 'LIVE',
        'fecha': '01 - Mayo - 2026',
        'evento': 'Cardenales vs Bravos',
        'hora_inicio': '19:00',
        'estadio': 'Estadio Monumental'
    }
    
    # Warning Song
    warning_song = {
        'titulo': 'Warning Song',
        'mensajes': [
            'Saludos a los aficionados',
            'Salen "Los Guartos"'
        ]
    }
    
    # Próximos contratos a vencer
    hoy = datetime.now().date()
    contratos = [
        {
            'cliente': 'Patrocinio completo',
            'tipo': 'Sponsor Principal',
            'fecha_vencimiento': datetime(2026, 4, 16).date(),
            'dias_restantes': (datetime(2026, 4, 16).date() - hoy).days,
            'monto': '$50,000'
        },
        {
            'cliente': 'Pantallas principales + Mencion del Animador',
            'tipo': 'Publicidad',
            'fecha_vencimiento': datetime(2026, 4, 16).date(),
            'dias_restantes': (datetime(2026, 4, 16).date() - hoy).days,
            'monto': '$25,000'
        },
        {
            'cliente': 'Zona VIP',
            'tipo': 'Patrocinio',
            'fecha_vencimiento': datetime(2026, 5, 30).date(),
            'dias_restantes': (datetime(2026, 5, 30).date() - hoy).days,
            'monto': '$35,000'
        }
    ]
    
    return render_template('dashboard/index.html',
                         usuarios_en_linea=usuarios_en_linea,
                         guion_actual=guion_actual,
                         warning_song=warning_song,
                         contratos=contratos)