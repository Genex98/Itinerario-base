"""
reportes_definition.py — ÚNICA FUENTE DE VERDAD para definiciones de reportes.

Cada módulo declara: campos, columnas, filtros, KPIs y placeholders analytics.
Todos los consumidores (backend, frontend, PDF, preview) leen de aquí.

FASE 3: creado como registro central. Los consumidores existentes se adaptan
gradualmente para leer de aquí en vez de CAMPOS_DISPONIBLES/COLUMNAS/COLUMNAS_PREVIEW.
"""

# ---------------------------------------------------------------------------
# Tipo de campo — mapea con CAMPOS_NUMERICOS y FORMATTERS de reportes_campos.py
# ---------------------------------------------------------------------------
TIPOS_CAMPO = {'texto', 'texto_largo', 'entero', 'decimal', 'moneda',
               'fecha', 'fecha_hora', 'boolean', 'porcentaje', 'duracion'}

AGGREGATES = {None, 'suma', 'promedio', 'min', 'max', 'conteo'}

# ---------------------------------------------------------------------------
# Definiciones por módulo
# ---------------------------------------------------------------------------
REPORT_DEFINITIONS = {}

# ── guiones ────────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['guiones'] = {
    'id': 'guiones',
    'titulo': 'REPORTE DE GUIONES',
    'descripcion': 'Análisis de guiones de show: estados, tiempos, elementos.',
    'fields': {
        'nombre':          {'label': 'Nombre',        'type': 'texto',      'width': 120, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'game':            {'label': 'Game',          'type': 'entero',     'width': 40,  'order': 2,  'groupable': False, 'sortable': True,  'aggregate': 'suma'},
        'pregame':         {'label': 'Pre-Game',      'type': 'entero',     'width': 40,  'order': 3,  'groupable': False, 'sortable': True,  'aggregate': 'suma'},
        'fecha_ejecucion': {'label': 'Ejecucion',     'type': 'fecha',      'width': 65,  'order': 4,  'groupable': False, 'sortable': True,  'aggregate': None},
        'estado':          {'label': 'Estado',        'type': 'texto',      'width': 65,  'order': 5,  'groupable': True,  'sortable': True,  'aggregate': None},
        'tiempo_total':    {'label': 'Tiempo',        'type': 'duracion',   'width': 55,  'order': 6,  'groupable': False, 'sortable': True,  'aggregate': 'promedio'},
    },
    'columns': [
        ('Nombre', 'nombre', 120), ('Game', 'game', 40), ('Pre-Game', 'pregame', 40),
        ('Ejecucion', 'fecha_ejecucion', 65), ('Estado', 'estado', 65), ('Tiempo', 'tiempo_total', 55),
    ],
    'default_columns': ['nombre', 'game', 'pregame', 'fecha_ejecucion', 'estado', 'tiempo_total'],
    'filters': {
        'estado':        {'label': 'Estado',        'type': 'select', 'options': [
            {'value': '', 'label': 'Todos'}, {'value': 'borrador', 'label': 'Borrador'},
            {'value': 'publicado', 'label': 'Publicado'}, {'value': 'en_vivo', 'label': 'En Vivo'},
            {'value': 'finalizado', 'label': 'Finalizado'},
        ]},
        'encargado':     {'label': 'Encargado',     'type': 'select', 'load_via': 'ajax'},
        'elementos_min': {'label': 'Elementos Min',  'type': 'number', 'placeholder': '0'},
        'elementos_max': {'label': 'Elementos Max',  'type': 'number', 'placeholder': '100'},
    },
    'kpi_cards': [
        {'key': 'total',       'label': 'Total',       'color': '#2563eb'},
        {'key': 'borradores',  'label': 'Borradores',  'color': '#f59e0b'},
        {'key': 'publicados',  'label': 'Publicados',  'color': '#10b981'},
        {'key': 'en_vivo',     'label': 'En Vivo',     'color': '#06b6d4'},
        {'key': 'finalizados', 'label': 'Finalizados', 'color': '#64748b'},
        {'key': 'tiempo_total','label': 'Tiempo Total', 'color': '#8b5cf6'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['estado'],
    },
}

# ── inventario ─────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['inventario'] = {
    'id': 'inventario',
    'titulo': 'REPORTE DE INVENTARIO',
    'descripcion': 'Catálogo de recursos: tipos, estados, costos, fechas de compra.',
    'fields': {
        'id':            {'label': 'ID',       'type': 'entero',   'width': 35,  'order': 1,  'groupable': False, 'sortable': True,  'aggregate': None},
        'nombre':        {'label': 'Nombre',   'type': 'texto',    'width': 120, 'order': 2,  'groupable': True,  'sortable': True,  'aggregate': None},
        'tipo_nombre':   {'label': 'Tipo',     'type': 'texto',    'width': 80,  'order': 3,  'groupable': True,  'sortable': True,  'aggregate': None},
        'estado_nombre': {'label': 'Estado',   'type': 'texto',    'width': 65,  'order': 4,  'groupable': True,  'sortable': True,  'aggregate': None},
        'fecha_compra':  {'label': 'Compra',   'type': 'fecha',    'width': 65,  'order': 5,  'groupable': False, 'sortable': True,  'aggregate': None},
        'costo':         {'label': 'Costo',    'type': 'moneda',   'width': 65,  'order': 6,  'groupable': False, 'sortable': True,  'aggregate': 'suma'},
    },
    'columns': [
        ('ID', 'id', 35), ('Nombre', 'nombre', 120), ('Tipo', 'tipo_nombre', 80),
        ('Estado', 'estado_nombre', 65), ('Compra', 'fecha_compra', 65), ('Costo', 'costo', 65),
    ],
    'default_columns': ['id', 'nombre', 'tipo_nombre', 'estado_nombre', 'fecha_compra'],
    'filters': {
        'tipo_nombre':   {'label': 'Tipo',     'type': 'select', 'load_via': 'ajax', 'progressive': ['estado_nombre']},
        'estado_nombre': {'label': 'Estado',   'type': 'select', 'load_via': 'ajax', 'depends_on': ['tipo_nombre']},
        'costo_min':     {'label': 'Costo Min','type': 'number', 'placeholder': '0'},
        'costo_max':     {'label': 'Costo Max','type': 'number', 'placeholder': '999999'},
    },
    'kpi_cards': [
        {'key': 'total',         'label': 'Total',         'color': '#2563eb'},
        {'key': 'costo_total',   'label': 'Costo Total',   'color': '#8b5cf6'},
        {'key': 'costo_promedio','label': 'Costo Promedio', 'color': '#06b6d4'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['tipo_nombre', 'estado_nombre'],
    },
}

# ── premios ────────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['premios'] = {
    'id': 'premios',
    'titulo': 'REPORTE DE PREMIOS',
    'descripcion': 'Inventario de premios: estados, patrocinadores, cantidades.',
    'fields': {
        'nombre':               {'label': 'Nombre',        'type': 'texto',      'width': 120, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'patrocinador_nombre':  {'label': 'Patrocinador',  'type': 'texto',      'width': 90,  'order': 2,  'groupable': True,  'sortable': True,  'aggregate': None},
        'estado':               {'label': 'Estado',        'type': 'texto',      'width': 55,  'order': 3,  'groupable': True,  'sortable': True,  'aggregate': None},
        'cantidad':             {'label': 'Total',         'type': 'entero',     'width': 35,  'order': 4,  'groupable': False, 'sortable': True,  'aggregate': 'suma'},
        'cantidad_entregada':   {'label': 'Entregados',    'type': 'entero',     'width': 40,  'order': 5,  'groupable': False, 'sortable': True,  'aggregate': 'suma'},
        'fecha_creacion':       {'label': 'Creacion',      'type': 'fecha',      'width': 65,  'order': 6,  'groupable': False, 'sortable': True,  'aggregate': None},
        'fecha_entrega':        {'label': 'Entrega',       'type': 'fecha_hora', 'width': 75,  'order': 7,  'groupable': False, 'sortable': True,  'aggregate': None},
    },
    'columns': [
        ('Nombre', 'nombre', 120), ('Patrocinador', 'patrocinador_nombre', 90),
        ('Estado', 'estado', 55), ('Total', 'cantidad', 35), ('Entreg.', 'cantidad_entregada', 40),
        ('Creacion', 'fecha_creacion', 65),
    ],
    'default_columns': ['nombre', 'patrocinador_nombre', 'estado', 'cantidad', 'cantidad_entregada', 'fecha_creacion'],
    'filters': {
        'estado':                {'label': 'Estado',        'type': 'select', 'options': [
            {'value': '', 'label': 'Todos'}, {'value': 'pendiente', 'label': 'Pendientes'},
            {'value': 'entregado', 'label': 'Entregados'},
        ], 'progressive': ['patrocinador_id']},
        'patrocinador_id':       {'label': 'Patrocinador',  'type': 'select', 'load_via': 'ajax', 'depends_on': ['estado']},
        'cantidad_min':          {'label': 'Cantidad Min',   'type': 'number', 'placeholder': '0'},
        'cantidad_max':          {'label': 'Cantidad Max',   'type': 'number', 'placeholder': '999'},
        'cantidad_entregada_min':{'label': 'Entregados Min', 'type': 'number', 'placeholder': '0'},
        'cantidad_entregada_max':{'label': 'Entregados Max', 'type': 'number', 'placeholder': '999'},
    },
    'kpi_cards': [
        {'key': 'total',       'label': 'Total',       'color': '#2563eb'},
        {'key': 'pendientes',  'label': 'Pendientes',  'color': '#f59e0b'},
        {'key': 'entregados',  'label': 'Entregados',  'color': '#10b981'},
        {'key': 'tasa_entrega','label': '% Entregado',  'color': '#06b6d4'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['estado', 'patrocinador_nombre'],
    },
}

# ── contratos ──────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['contratos'] = {
    'id': 'contratos',
    'titulo': 'REPORTE DE CONTRATOS',
    'descripcion': 'Contratos de patrocinio: tipos, montos, vigencia, estados.',
    'fields': {
        'nombre_empresa': {'label': 'Patrocinador',   'type': 'texto',    'width': 110, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'tipo':           {'label': 'Tipo',           'type': 'texto',    'width': 55,  'order': 2,  'groupable': True,  'sortable': True,  'aggregate': None},
        'estatus':        {'label': 'Estatus',        'type': 'texto',    'width': 55,  'order': 3,  'groupable': True,  'sortable': True,  'aggregate': None},
        'monto_total':    {'label': 'Monto',          'type': 'moneda',   'width': 65,  'order': 4,  'groupable': False, 'sortable': True,  'aggregate': 'suma'},
        'fecha_inicio':   {'label': 'Inicio',         'type': 'fecha',    'width': 65,  'order': 5,  'groupable': False, 'sortable': True,  'aggregate': None},
        'fecha_fin':      {'label': 'Fin',            'type': 'fecha',    'width': 65,  'order': 6,  'groupable': False, 'sortable': True,  'aggregate': None},
        'dias_restantes': {'label': 'Dias',           'type': 'entero',   'width': 40,  'order': 7,  'groupable': False, 'sortable': True,  'aggregate': 'promedio'},
    },
    'columns': [
        ('Patrocinador', 'nombre_empresa', 110), ('Tipo', 'tipo', 55), ('Estatus', 'estatus', 55),
        ('Monto', 'monto_total', 65), ('Inicio', 'fecha_inicio', 65), ('Fin', 'fecha_fin', 65),
        ('Dias', 'dias_restantes', 40),
    ],
    'default_columns': ['nombre_empresa', 'tipo', 'estatus', 'fecha_inicio', 'fecha_fin', 'dias_restantes', 'monto_total'],
    'filters': {
        'tipo':            {'label': 'Tipo',         'type': 'select', 'options': [
            {'value': '', 'label': 'Todos los tipos'}, {'value': '1', 'label': 'Bronce'},
            {'value': '2', 'label': 'Plata'}, {'value': '3', 'label': 'Oro'},
        ], 'progressive': ['patrocinador_id']},
        'estatus':         {'label': 'Estatus',      'type': 'select', 'options': [
            {'value': '', 'label': 'Todos los estados'}, {'value': 'Vigente', 'label': 'Vigentes'},
            {'value': 'Vencido', 'label': 'Vencidos'}, {'value': 'Borrador', 'label': 'Borradores'},
        ]},
        'patrocinador_id': {'label': 'Patrocinador', 'type': 'select', 'load_via': 'ajax', 'depends_on': ['tipo']},
        'monto_min':       {'label': 'Monto Min',    'type': 'number', 'placeholder': '0'},
        'monto_max':       {'label': 'Monto Max',    'type': 'number', 'placeholder': '999999'},
    },
    'kpi_cards': [
        {'key': 'total',              'label': 'Total',       'color': '#2563eb'},
        {'key': 'vigentes',           'label': 'Vigentes',    'color': '#10b981'},
        {'key': 'vencidos',           'label': 'Vencidos',    'color': '#ef4444'},
        {'key': 'borradores',         'label': 'Borradores',  'color': '#f59e0b'},
        {'key': 'monto_total',        'label': 'Monto Total', 'color': '#2563eb'},
        {'key': 'monto_promedio',     'label': 'Promedio',    'color': '#06b6d4'},
        {'key': 'vigentes_porcentaje','label': '% Vigentes',   'color': '#10b981'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['tipo', 'estatus'],
    },
}

# ── balance ────────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['balance'] = {
    'id': 'balance',
    'titulo': 'REPORTE DE BALANCE',
    'descripcion': 'Historial de pagos: montos, tipos de pago, patrocinadores.',
    'fields': {
        'nombre_patrocinador': {'label': 'Patrocinador', 'type': 'texto',  'width': 110, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'tipo_pago':           {'label': 'Tipo Pago',   'type': 'texto',  'width': 65,  'order': 2,  'groupable': True,  'sortable': True,  'aggregate': None},
        'monto':               {'label': 'Monto',       'type': 'moneda', 'width': 65,  'order': 3,  'groupable': False, 'sortable': True,  'aggregate': 'suma'},
        'referencia':          {'label': 'Referencia',  'type': 'texto',  'width': 80,  'order': 4,  'groupable': False, 'sortable': True,  'aggregate': None},
        'fecha_pago':          {'label': 'Fecha Pago',  'type': 'fecha',  'width': 65,  'order': 5,  'groupable': False, 'sortable': True,  'aggregate': None},
    },
    'columns': [
        ('Patrocinador', 'nombre_patrocinador', 110), ('Tipo Pago', 'tipo_pago', 65),
        ('Monto', 'monto', 65), ('Referencia', 'referencia', 80), ('Fecha Pago', 'fecha_pago', 65),
    ],
    'default_columns': ['nombre_patrocinador', 'tipo_pago', 'monto', 'referencia', 'fecha_pago'],
    'filters': {
        'tipo_pago':      {'label': 'Tipo Pago',    'type': 'select', 'load_via': 'ajax'},
        'patrocinador_id':{'label': 'Patrocinador', 'type': 'select', 'load_via': 'ajax'},
        'monto_min':      {'label': 'Monto Min',    'type': 'number', 'placeholder': '0'},
        'monto_max':      {'label': 'Monto Max',    'type': 'number', 'placeholder': '999999'},
    },
    'kpi_cards': [
        {'key': 'total_pagos', 'label': 'Total Pagos',  'color': '#2563eb'},
        {'key': 'monto_total', 'label': 'Monto Total',  'color': '#8b5cf6'},
        {'key': 'promedio',    'label': 'Promedio',      'color': '#06b6d4'},
        {'key': 'monto_min',   'label': 'Monto Min',     'color': '#64748b'},
        {'key': 'monto_max',   'label': 'Monto Max',     'color': '#64748b'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['tipo_pago'],
    },
}

# ── tareas ─────────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['tareas'] = {
    'id': 'tareas',
    'titulo': 'REPORTE DE TAREAS',
    'descripcion': 'Tareas asignadas: estados, responsables, fechas.',
    'fields': {
        'nombre_tarea':           {'label': 'Tarea',      'type': 'texto',      'width': 150, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'estado':                 {'label': 'Estado',     'type': 'texto',      'width': 65,  'order': 2,  'groupable': True,  'sortable': True,  'aggregate': None},
        'asignado_a':             {'label': 'Asignado a', 'type': 'texto',      'width': 80,  'order': 3,  'groupable': True,  'sortable': True,  'aggregate': None},
        'fecha_asignacion_tarea': {'label': 'Fecha',      'type': 'fecha_hora', 'width': 75,  'order': 4,  'groupable': False, 'sortable': True,  'aggregate': None},
    },
    'columns': [
        ('Tarea', 'nombre_tarea', 150), ('Estado', 'estado', 65),
        ('Asignado a', 'asignado_a', 80), ('Fecha', 'fecha_asignacion_tarea', 75),
    ],
    'default_columns': ['nombre_tarea', 'estado', 'asignado_a', 'fecha_asignacion_tarea'],
    'filters': {
        'estado':     {'label': 'Estado',    'type': 'select', 'options': [
            {'value': '', 'label': 'Todos'}, {'value': 'Pendiente', 'label': 'Pendientes'},
            {'value': 'En Progreso', 'label': 'En Progreso'}, {'value': 'Completada', 'label': 'Completadas'},
        ]},
        'asignado_a': {'label': 'Asignado',  'type': 'select', 'load_via': 'ajax'},
        'usuario_id': {'label': 'Usuario',   'type': 'select', 'load_via': 'ajax'},
    },
    'kpi_cards': [
        {'key': 'total',          'label': 'Total',      'color': '#2563eb'},
        {'key': 'pendientes',     'label': 'Pendientes',  'color': '#f59e0b'},
        {'key': 'en_progreso',    'label': 'En Progreso', 'color': '#06b6d4'},
        {'key': 'completadas',    'label': 'Completadas',  'color': '#10b981'},
        {'key': 'completadas_pct','label': '% Completo',   'color': '#8b5cf6'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['estado'],
    },
}

# ── patrocinadores ─────────────────────────────────────────────────────────
REPORT_DEFINITIONS['patrocinadores'] = {
    'id': 'patrocinadores',
    'titulo': 'REPORTE DE PATROCINADORES',
    'descripcion': 'Directorio de patrocinadores: datos de contacto, contratos.',
    'fields': {
        'nombre_empresa': {'label': 'Empresa',   'type': 'texto',    'width': 110, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'rif':            {'label': 'RIF',       'type': 'texto',    'width': 75,  'order': 2,  'groupable': False, 'sortable': True,  'aggregate': None},
        'telefono':       {'label': 'Telefono',  'type': 'texto',    'width': 70,  'order': 3,  'groupable': False, 'sortable': True,  'aggregate': None},
        'tipo_contrato':  {'label': 'Contrato',  'type': 'texto',    'width': 65,  'order': 4,  'groupable': True,  'sortable': True,  'aggregate': None},
        'estado':         {'label': 'Activo',    'type': 'boolean',  'width': 55,  'order': 5,  'groupable': True,  'sortable': True,  'aggregate': None},
    },
    'columns': [
        ('Empresa', 'nombre_empresa', 110), ('RIF', 'rif', 75), ('Telefono', 'telefono', 70),
        ('Contrato', 'tipo_contrato', 65), ('Activo', 'estado', 55),
    ],
    'default_columns': ['nombre_empresa', 'rif', 'telefono', 'tipo_contrato'],
    'filters': {
        'tipo_contrato': {'label': 'Contrato', 'type': 'select', 'options': [
            {'value': '', 'label': 'Todos'}, {'value': 'Bronce', 'label': 'Bronce'},
            {'value': 'Plata', 'label': 'Plata'}, {'value': 'Oro', 'label': 'Oro'},
        ]},
        'estado_pat':    {'label': 'Estado',   'type': 'select', 'options': [
            {'value': '', 'label': 'Todos'}, {'value': '1', 'label': 'Activos'},
            {'value': '0', 'label': 'Inactivos'},
        ]},
    },
    'kpi_cards': [
        {'key': 'total',    'label': 'Total',    'color': '#2563eb'},
        {'key': 'activos',  'label': 'Activos',  'color': '#10b981'},
        {'key': 'inactivos','label': 'Inactivos', 'color': '#ef4444'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['tipo_contrato', 'estado'],
    },
}

# ── usuarios ───────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['usuarios'] = {
    'id': 'usuarios',
    'titulo': 'REPORTE DE USUARIOS',
    'descripcion': 'Directorio de usuarios: roles, departamentos, estados.',
    'fields': {
        'nombre':       {'label': 'Nombre',     'type': 'texto',   'width': 110, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'email':        {'label': 'Email',      'type': 'texto',   'width': 120, 'order': 2,  'groupable': False, 'sortable': True,  'aggregate': None},
        'rol':          {'label': 'Rol',        'type': 'texto',   'width': 70,  'order': 3,  'groupable': True,  'sortable': True,  'aggregate': None},
        'departamento': {'label': 'Depto',      'type': 'texto',   'width': 70,  'order': 4,  'groupable': True,  'sortable': True,  'aggregate': None},
        'activo':       {'label': 'Activo',     'type': 'boolean', 'width': 55,  'order': 5,  'groupable': True,  'sortable': True,  'aggregate': None},
    },
    'columns': [
        ('Nombre', 'nombre', 110), ('Email', 'email', 120), ('Rol', 'rol', 70),
        ('Depto', 'departamento', 70), ('Estado', 'activo', 55),
    ],
    'default_columns': ['nombre', 'email', 'rol', 'departamento', 'activo'],
    'filters': {
        'departamento': {'label': 'Depto',   'type': 'select', 'load_via': 'ajax'},
        'rol':          {'label': 'Rol',     'type': 'select', 'load_via': 'ajax'},
        'activo':       {'label': 'Estado',  'type': 'select', 'options': [
            {'value': '', 'label': 'Todos'}, {'value': '1', 'label': 'Activos'},
            {'value': '0', 'label': 'Inactivos'},
        ]},
    },
    'kpi_cards': [
        {'key': 'total',     'label': 'Total',     'color': '#2563eb'},
        {'key': 'activos',   'label': 'Activos',   'color': '#10b981'},
        {'key': 'inactivos', 'label': 'Inactivos',  'color': '#ef4444'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['rol', 'departamento'],
    },
}

# ── mantenimiento ──────────────────────────────────────────────────────────
REPORT_DEFINITIONS['mantenimiento'] = {
    'id': 'mantenimiento',
    'titulo': 'REPORTE DE MANTENIMIENTO',
    'descripcion': 'Órdenes de mantenimiento: recursos, diagnósticos, tiempos.',
    'fields': {
        'recurso_nombre': {'label': 'Recurso',     'type': 'texto',      'width': 110, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'estado':         {'label': 'Estado',      'type': 'texto',      'width': 65,  'order': 2,  'groupable': True,  'sortable': True,  'aggregate': None},
        'fecha_ingreso':  {'label': 'Ingreso',     'type': 'fecha',      'width': 65,  'order': 3,  'groupable': False, 'sortable': True,  'aggregate': None},
        'diagnostico':    {'label': 'Diagnostico', 'type': 'texto_largo','width': 130, 'order': 4,  'groupable': False, 'sortable': False, 'aggregate': None},
        'dias_en_taller': {'label': 'Dias',        'type': 'entero',     'width': 45,  'order': 5,  'groupable': False, 'sortable': True,  'aggregate': 'promedio'},
    },
    'columns': [
        ('Recurso', 'recurso_nombre', 110), ('Estado', 'estado', 65),
        ('Ingreso', 'fecha_ingreso', 65), ('Diagnostico', 'diagnostico', 130),
    ],
    'default_columns': ['recurso_nombre', 'estado', 'fecha_ingreso', 'diagnostico'],
    'filters': {
        'estado':      {'label': 'Estado',    'type': 'select', 'options': [
            {'value': '', 'label': 'Todos'}, {'value': 'en_espera', 'label': 'En Espera'},
            {'value': 'en_reparacion', 'label': 'En Reparacion'}, {'value': 'reparado', 'label': 'Reparados'},
            {'value': 'baja', 'label': 'Dados de Baja'},
        ]},
        'recurso_id':  {'label': 'Recurso',   'type': 'select', 'load_via': 'ajax'},
        'dias_min':    {'label': 'Dias Min',   'type': 'number', 'placeholder': '0'},
        'dias_max':    {'label': 'Dias Max',   'type': 'number', 'placeholder': '999'},
    },
    'kpi_cards': [
        {'key': 'total',          'label': 'Total',          'color': '#2563eb'},
        {'key': 'en_espera',      'label': 'En Espera',      'color': '#f59e0b'},
        {'key': 'en_reparacion',  'label': 'En Reparacion',   'color': '#06b6d4'},
        {'key': 'reparados',      'label': 'Reparados',       'color': '#10b981'},
        {'key': 'dados_baja',     'label': 'Dados de Baja',   'color': '#ef4444'},
        {'key': 'promedio_dias',  'label': 'Prom. Dias',      'color': '#8b5cf6'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['estado'],
    },
}

# ── reels ──────────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['reels'] = {
    'id': 'reels',
    'titulo': 'REPORTE DE REELS',
    'descripcion': 'Reels de video: duración, patrocinadores, cantidad de videos.',
    'fields': {
        'nombre':       {'label': 'Nombre',      'type': 'texto',      'width': 120, 'order': 1,  'groupable': True,  'sortable': True,  'aggregate': None},
        'patrocinado':  {'label': 'Patrocinador', 'type': 'texto',     'width': 100, 'order': 2,  'groupable': True,  'sortable': True,  'aggregate': None},
        'videos_count': {'label': 'Videos',      'type': 'entero',     'width': 40,  'order': 3,  'groupable': False, 'sortable': True,  'aggregate': 'suma'},
        'duracion':     {'label': 'Duracion',    'type': 'texto',      'width': 55,  'order': 4,  'groupable': False, 'sortable': False, 'aggregate': None},
        'creado_en':    {'label': 'Creacion',    'type': 'fecha_hora', 'width': 80,  'order': 5,  'groupable': False, 'sortable': True,  'aggregate': None},
    },
    'columns': [],  # reels usa layout especial (KeepTogether cards)
    'default_columns': ['nombre', 'patrocinado', 'videos_count', 'duracion'],
    'filters': {
        'patrocinador_id': {'label': 'Patrocinador',   'type': 'select', 'load_via': 'ajax'},
        'duracion_min':    {'label': 'Duracion Min (s)','type': 'number', 'placeholder': '0'},
        'duracion_max':    {'label': 'Duracion Max (s)','type': 'number', 'placeholder': '3600'},
    },
    'kpi_cards': [
        {'key': 'total',           'label': 'Total Reels',    'color': '#2563eb'},
        {'key': 'total_videos',    'label': 'Total Videos',   'color': '#06b6d4'},
        {'key': 'duracion_total',  'label': 'Duracion Total', 'color': '#8b5cf6'},
        {'key': 'duracion_promedio','label': 'Duracion Prom.', 'color': '#64748b'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['patrocinado'],
    },
    '_layout': 'custom',  # reels tiene layout especial, no usa tabla estándar
}

# ── bitacora ───────────────────────────────────────────────────────────────
REPORT_DEFINITIONS['bitacora'] = {
    'id': 'bitacora',
    'titulo': 'REPORTE DE ACTIVIDAD / BITACORA',
    'descripcion': 'Registro de actividad del sistema: acciones, usuarios, módulos.',
    'fields': {
        'id':             {'label': '#',         'type': 'entero',     'width': 35,  'order': 1,  'groupable': False, 'sortable': True,  'aggregate': None},
        'usuario_nombre': {'label': 'Usuario',  'type': 'texto',      'width': 100, 'order': 2,  'groupable': True,  'sortable': True,  'aggregate': None},
        'tipo_accion':    {'label': 'Accion',   'type': 'texto',      'width': 55,  'order': 3,  'groupable': True,  'sortable': True,  'aggregate': None},
        'modulo':         {'label': 'Modulo',   'type': 'texto',      'width': 75,  'order': 4,  'groupable': True,  'sortable': True,  'aggregate': None},
        'detalle':        {'label': 'Detalle',  'type': 'texto_largo','width': 130, 'order': 5,  'groupable': False, 'sortable': False, 'aggregate': None},
        'created_at':     {'label': 'Fecha',    'type': 'fecha_hora', 'width': 80,  'order': 6,  'groupable': False, 'sortable': True,  'aggregate': None},
    },
    'columns': [
        ('#', 'id', 35), ('Usuario', 'usuario_nombre', 100), ('Accion', 'tipo_accion', 55),
        ('Modulo', 'modulo', 75), ('Detalle', 'detalle', 130), ('Fecha', 'created_at', 80),
    ],
    'default_columns': ['id', 'usuario_nombre', 'tipo_accion', 'modulo', 'detalle', 'created_at'],
    'filters': {
        'usuario_id':    {'label': 'Usuario',  'type': 'select', 'load_via': 'ajax'},
        'tipo_accion':   {'label': 'Accion',   'type': 'select', 'load_via': 'ajax'},
        'modulo_filter': {'label': 'Modulo',   'type': 'select', 'load_via': 'ajax'},
    },
    'kpi_cards': [
        {'key': 'total',        'label': 'Total',        'color': '#2563eb'},
        {'key': 'creaciones',   'label': 'Creaciones',    'color': '#10b981'},
        {'key': 'ediciones',    'label': 'Ediciones',     'color': '#06b6d4'},
        {'key': 'eliminaciones','label': 'Eliminaciones',  'color': '#ef4444'},
    ],
    'analytics': {
        'tendencias': [], 'alertas': [], 'rankings': [],
        'distribuciones': ['tipo_accion', 'modulo'],
    },
}


# ---------------------------------------------------------------------------
# ADAPTADORES — backward compatibility con consumidores existentes
# ---------------------------------------------------------------------------

def get_definition(modulo):
    """Retorna la definición completa de un módulo."""
    return REPORT_DEFINITIONS.get(modulo)


def get_fields(modulo):
    """Retorna fields como dict {key: field_dict} — reemplaza CAMPOS_DISPONIBLES."""
    defn = REPORT_DEFINITIONS.get(modulo)
    return defn['fields'] if defn else {}


def get_columns_tuple(modulo):
    """Retorna columns como [(label, key, width), ...] — reemplaza COLUMNAS de generators."""
    defn = REPORT_DEFINITIONS.get(modulo)
    return defn.get('columns', []) if defn else []


def get_default_columns(modulo):
    """Retorna default_columns como [key, ...] — reemplaza COLUMNAS_DEFAULT."""
    defn = REPORT_DEFINITIONS.get(modulo)
    return defn.get('default_columns', []) if defn else []


def get_columns_preview(modulo):
    """Retorna columns como [{key, label}, ...] — reemplaza COLUMNAS_PREVIEW."""
    defn = REPORT_DEFINITIONS.get(modulo)
    if not defn:
        return []
    return [{'key': c[1], 'label': c[0]} for c in defn.get('columns', [])]


def get_filters(modulo):
    """Retorna filters dict — reemplaza FILTROS_PERMITIDOS + MODULE_CONFIG.filters."""
    defn = REPORT_DEFINITIONS.get(modulo)
    return defn.get('filters', {}) if defn else {}


def get_filters_keys(modulo):
    """Retorna set de keys de filtros — reemplaza FILTROS_PERMITIDOS."""
    defn = REPORT_DEFINITIONS.get(modulo)
    if not defn:
        return set()
    return set(defn.get('filters', {}).keys())


def get_kpi_cards(modulo):
    """Retorna kpiCards — reemplaza MODULE_CONFIG.kpiCards."""
    defn = REPORT_DEFINITIONS.get(modulo)
    return defn.get('kpi_cards', []) if defn else []


def get_field_type(modulo, key):
    """Retorna el type de un campo — reemplaza CAMPOS_DISPONIBLES[key]['type']."""
    fields = get_fields(modulo)
    campo = fields.get(key, {})
    return campo.get('type', 'texto')


def is_numeric(modulo, key):
    """True si el campo es numérico para agregación — reemplaza _es_numerico()."""
    from app.helpers.reportes_campos import CAMPOS_NUMERICOS
    return get_field_type(modulo, key) in CAMPOS_NUMERICOS


def format_cell(modulo, key, value):
    """Formatea un valor de celda según el tipo — reemplaza _formatear_celda()."""
    from app.helpers.reportes_campos import FORMATTERS
    tipo = get_field_type(modulo, key)
    formatter = FORMATTERS.get(tipo, FORMATTERS['texto'])
    return formatter(value)


def get_all_modules():
    """Retorna lista de IDs de todos los módulos."""
    return list(REPORT_DEFINITIONS.keys())
