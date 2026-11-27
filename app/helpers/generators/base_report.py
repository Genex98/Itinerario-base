import io
import os
from datetime import datetime
from collections import OrderedDict
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.helpers.reportes_analytics import Severity


class BaseReportGenerator:
    MODULO = ''
    TITULO = ''
    COLUMNAS = []

    def __init__(self, usuario_actual):
        self.usuario = usuario_actual
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.style_titulo = ParagraphStyle(
            'TituloReporte', parent=self.styles['Heading1'],
            fontSize=18, leading=22,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=6,
        )
        self.style_normal = self.styles['Normal']
        self.style_bold = ParagraphStyle(
            'TextoNegrita', parent=self.style_normal, fontName='Helvetica-Bold'
        )
        self.style_small = ParagraphStyle(
            'TextoSmall', parent=self.style_normal, fontSize=8,
            textColor=colors.HexColor('#64748b')
        )

    # ── Métodos para columnas dinámicas ──────────────────────────────

    def _obtener_columnas(self, opciones):
        """Resuelve qué columnas usar: dinámicas o default."""
        col_ids = (opciones or {}).get('columnas_seleccionadas')
        if not col_ids:
            return self.COLUMNAS

        from app.helpers.reportes_definition import get_fields
        campos = get_fields(self.MODULO)
        columnas = []
        for key in col_ids:
            if key in campos:
                c = campos[key]
                columnas.append((c['label'], key, c['width']))
        return columnas if columnas else self.COLUMNAS

    def _calcular_anchos(self, columnas, orientacion='vertical'):
        """Anchos proporcionales que caben en la página."""
        disponible = 712 if orientacion == 'horizontal' else 532
        anchos = [c[2] for c in columnas]
        total = sum(anchos)
        if total <= disponible:
            return anchos
        factor = disponible / total
        return [max(30, int(a * factor)) for a in anchos]

    def _determinar_pagina(self, columnas, orientacion_solicitada):
        """Determina tamaño y orientación de página."""
        if orientacion_solicitada == 'horizontal':
            return landscape(letter)
        total_width = sum(c[2] for c in columnas)
        if len(columnas) >= 8 or total_width > 500:
            return landscape(letter)
        return letter

    def _ajustar_estilo_segun_columnas(self, num_columnas):
        """Ajusta tamaños de fuente según cantidad de columnas."""
        if num_columnas <= 7:
            return
        elif num_columnas <= 10:
            self.style_normal.fontSize = 7
            self.style_bold = ParagraphStyle(
                'TextoNegrita7', parent=self.style_normal, fontName='Helvetica-Bold'
            )
        else:
            self.style_normal.fontSize = 6
            self.style_bold = ParagraphStyle(
                'TextoNegrita6', parent=self.style_normal, fontName='Helvetica-Bold'
            )

    def _tipo_campo(self, key):
        """Obtiene el tipo de campo desde el registro central."""
        from app.helpers.reportes_definition import get_field_type
        return get_field_type(self.MODULO, key)

    def _es_numerico(self, key):
        """True si el campo se puede sumar en subtotales."""
        from app.helpers.reportes_definition import is_numeric
        return is_numeric(self.MODULO, key)

    def _formatear_celda(self, item, columna, tipo_campo):
        """Formatea un valor según tipo de campo."""
        from app.helpers.reportes_definition import format_cell
        key = columna[1]
        value = item.get(key)
        texto = format_cell(self.MODULO, key, value)
        max_chars = max(10, columna[2] // 5)
        if len(texto) > max_chars:
            texto = texto[:max_chars - 2] + '..'
        return Paragraph(texto, self.style_normal)

    def _construir_tabla_simple(self, datos, columnas):
        """Tabla sin agrupar: header + filas."""
        header = [Paragraph(f"<b>{c[0]}</b>", self.style_bold) for c in columnas]
        rows = [header]
        for item in datos:
            rows.append([
                self._formatear_celda(item, c, self._tipo_campo(c[1]))
                for c in columnas
            ])
        return rows

    def _construir_tabla_agrupada(self, datos, columnas, campo_agrupacion):
        """Tabla con grupos, subtotales y total general."""
        grupos = OrderedDict()
        for item in datos:
            valor = item.get(campo_agrupacion, 'Sin valor')
            grupos.setdefault(valor, []).append(item)

        numeric_keys = [c[1] for c in columnas if self._es_numerico(c[1])]
        total_general = {k: 0.0 for k in numeric_keys}
        rows = []

        for grupo_valor, items in grupos.items():
            rows.append([
                Paragraph(f"<b>{grupo_valor}</b>", self.style_bold)
            ] + [''] * (len(columnas) - 1))

            for item in items:
                rows.append([
                    self._formatear_celda(item, c, self._tipo_campo(c[1]))
                    for c in columnas
                ])

            subtotales = {}
            for k in numeric_keys:
                subtotales[k] = sum(float(i.get(k, 0) or 0) for i in items)
                total_general[k] += subtotales[k]

            subtotal_row = [Paragraph("<b>Subtotal</b>", self.style_bold)]
            for c in columnas[1:]:
                val = subtotales.get(c[1])
                if val is not None and val != 0:
                    subtotal_row.append(
                        Paragraph(f"<b>${val:,.2f}</b>" if self._tipo_campo(c[1]) == 'moneda'
                                  else f"<b>{val:,.1f}</b>" if self._tipo_campo(c[1]) == 'decimal'
                                  else f"<b>{int(val):,}</b>",
                                  self.style_bold))
                else:
                    subtotal_row.append('')
            rows.append(subtotal_row)

        total_row = [Paragraph("<b>TOTAL GENERAL</b>", self.style_bold)]
        for c in columnas[1:]:
            val = total_general.get(c[1])
            if val and val != 0:
                total_row.append(
                    Paragraph(f"<b>${val:,.2f}</b>" if self._tipo_campo(c[1]) == 'moneda'
                              else f"<b>{val:,.1f}</b>" if self._tipo_campo(c[1]) == 'decimal'
                              else f"<b>{int(val):,}</b>",
                              self.style_bold))
            else:
                total_row.append('')
        rows.append(total_row)

        return rows

    def _post_table_sections(self, kpis, opciones):
        """Hook para distribuciones. Override en subclases."""
        return []

    # ── Secciones de Analítica (FASE 4E) ───────────────────────────

    def _seccion_analytics(self, analytics_result):
        """Renderiza AnalyticsResult completo: KPIs + alertas + insights + rankings + distribuciones + tendencias."""
        story = []
        if not analytics_result:
            return story

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e40af'), spaceAfter=6))
        story.append(Paragraph("<b>Análisis Detallado</b>", self.style_normal))
        story.append(Spacer(1, 6))

        # KPIs
        if analytics_result.metrics:
            story.extend(self._analytics_kpis(analytics_result.metrics))

        # Alertas
        if analytics_result.alerts:
            story.extend(self._analytics_alertas(analytics_result.alerts))

        # Insights
        if analytics_result.insights:
            story.extend(self._analytics_insights(analytics_result.insights))

        # Rankings
        if analytics_result.rankings:
            story.extend(self._analytics_rankings(analytics_result.rankings))

        # Distribuciones
        if analytics_result.distributions:
            story.extend(self._analytics_distributions(analytics_result.distributions))

        # Tendencias
        if analytics_result.trends:
            story.extend(self._analytics_trends(analytics_result.trends))

        return story

    def _analytics_kpis(self, metrics):
        story = []
        label_map = {
            'total': 'Total', 'vigentes': 'Vigentes', 'vencidos': 'Vencidos',
            'borradores': 'Borradores', 'vigentes_pct': '% Vigentes',
            'monto_total': 'Monto Total', 'monto_promedio': 'Monto Promedio',
            'monto_min': 'Monto Mín.', 'monto_max': 'Monto Máx.',
            'total_pagos': 'Total Pagos', 'activos': 'Activos',
            'inactivos': 'Inactivos', 'activos_pct': '% Activos',
            'en_espera': 'En Espera', 'en_reparacion': 'En Reparación',
            'reparados': 'Reparados', 'dados_baja': 'Dados de Baja',
            'promedio_dias': 'Días Prom.', 'max_dias': 'Máx. Días',
            'min_dias': 'Mín. Días', 'pendientes': 'Pendientes',
            'en_progreso': 'En Progreso', 'completadas': 'Completadas',
            'completadas_pct': '% Completadas', 'total_cantidad': 'Cantidad Total',
            'total_entregada': 'Entregada', 'tasa_entrega': '% Entrega',
            'brecha': 'Brecha', 'costo_total': 'Costo Total',
            'costo_promedio': 'Costo Prom.', 'costo_min': 'Costo Mín.',
            'costo_max': 'Costo Máx.', 'publicados': 'Publicados',
            'en_vivo': 'En Vivo', 'finalizados': 'Finalizados',
            'tiempo_total': 'Tiempo Total', 'tiempo_promedio': 'Tiempo Prom.',
            'tiempo_min': 'Tiempo Mín.', 'tiempo_max': 'Tiempo Máx.',
            'total_game': 'Game', 'total_pregame': 'Pre-game',
            'creaciones': 'Creaciones', 'ediciones': 'Ediciones',
            'eliminaciones': 'Eliminaciones', 'duracion_total': 'Duración Total',
            'duracion_promedio': 'Duración Prom.', 'videos_por_reel': 'Videos/Reel',
        }
        for m in metrics:
            if m.key == 'total' and not isinstance(m.value, (int, float)):
                continue
            if isinstance(m.value, dict):
                continue
            label = label_map.get(m.key, m.key.replace('_', ' ').title())
            try:
                if m.unit == 'currency' and isinstance(m.value, (int, float)):
                    value = f"${m.value:,.0f}"
                elif m.unit == 'percent' and isinstance(m.value, (int, float)):
                    value = f"{m.value:.1f}%"
                elif m.unit == 'seconds' and isinstance(m.value, (int, float)):
                    h, rem = divmod(int(m.value), 3600)
                    mins, secs = divmod(rem, 60)
                    value = f"{h}h {mins}m" if h else f"{mins}m {secs}s"
                elif m.unit == 'days' and isinstance(m.value, (int, float)):
                    value = f"{m.value:.1f} días"
                elif isinstance(m.value, int):
                    value = f"{m.value:,}"
                elif isinstance(m.value, float):
                    value = f"{m.value:,.1f}"
                else:
                    value = str(m.value)
            except (ValueError, TypeError):
                value = str(m.value)
            story.append(Paragraph(
                f"<font size='8' color='#475569'><b>{label}:</b> {value}</font>",
                self.style_normal
            ))
        story.append(Spacer(1, 6))
        return story

    def _analytics_alertas(self, alerts):
        story = []
        severity_color = {
            Severity.CRITICAL: '#dc2626',
            Severity.WARNING: '#d97706',
            Severity.INFO: '#2563eb',
        }
        severity_bg = {
            Severity.CRITICAL: '#fef2f2',
            Severity.WARNING: '#fffbeb',
            Severity.INFO: '#eff6ff',
        }
        severity_label = {
            Severity.CRITICAL: 'CRÍTICO',
            Severity.WARNING: 'ALERTA',
            Severity.INFO: 'INFO',
        }
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=4))
        story.append(Paragraph("<b>Alertas Activas</b>", self.style_normal))
        story.append(Spacer(1, 4))
        for alert in alerts:
            if alert.severity not in (Severity.CRITICAL, Severity.WARNING, Severity.INFO):
                continue
            color = severity_color.get(alert.severity, '#64748b')
            bg = severity_bg.get(alert.severity, '#f8fafc')
            label = severity_label.get(alert.severity, '?')
            count_text = f" ({alert.affected_count} afectados)" if alert.affected_count else ""
            story.append(Paragraph(
                f"<font size='8' color='{color}'><b>[{label}]</b> {alert.title}{count_text}</font>",
                self.style_normal
            ))
            if alert.description:
                story.append(Paragraph(
                    f"<font size='7' color='#64748b'>  {alert.description}</font>",
                    self.style_normal
                ))
        story.append(Spacer(1, 6))
        return story

    def _analytics_insights(self, insights):
        story = []
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=4))
        story.append(Paragraph("<b>Hallazgos Clave</b>", self.style_normal))
        story.append(Spacer(1, 4))
        for insight in insights[:5]:
            story.append(Paragraph(
                f"<font size='8' color='#334155'>• {insight.text}</font>",
                self.style_normal
            ))
        story.append(Spacer(1, 6))
        return story

    def _analytics_rankings(self, rankings):
        story = []
        for ranking in rankings[:2]:
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=4))
            story.append(Paragraph(f"<b>{ranking.label}</b>", self.style_normal))
            story.append(Spacer(1, 4))
            header = [Paragraph("<b>#</b>", self.style_bold),
                      Paragraph("<b>Item</b>", self.style_bold),
                      Paragraph("<b>Valor</b>", self.style_bold)]
            rows = [header]
            for i, item in enumerate(ranking.items[:5], 1):
                val = f"{item.value:,}" if isinstance(item.value, (int, float)) else str(item.value)
                rows.append([
                    Paragraph(str(i), self.style_normal),
                    Paragraph(str(item.item)[:30], self.style_normal),
                    Paragraph(val, self.style_normal),
                ])
            t = Table(rows, colWidths=[40, 200, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))
        return story

    def _analytics_distributions(self, distributions):
        story = []
        for dist in distributions[:3]:
            items = [(d.category, d.count) for d in dist.items]
            story.extend(self._seccion_distribucion(dist.label, items))
        return story

    def _analytics_trends(self, trends):
        story = []
        for trend in trends[:2]:
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=4))
            story.append(Paragraph(f"<b>{trend.label}</b>", self.style_normal))
            story.append(Spacer(1, 4))
            if trend.data:
                header = [Paragraph("<b>Período</b>", self.style_bold),
                          Paragraph("<b>Valor</b>", self.style_bold)]
                rows = [header]
                for p in trend.data[-6:]:
                    rows.append([
                        Paragraph(str(p.period), self.style_normal),
                        Paragraph(str(p.value), self.style_normal),
                    ])
                t = Table(rows, colWidths=[200, 100])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('PADDING', (0, 0), (-1, -1), 4),
                    ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#e2e8f0')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ]))
                story.append(t)
                story.append(Spacer(1, 6))
        return story

    # ── Header ───────────────────────────────────────────────────────
    def _header(self, filtros=None):
        story = []
        usuario_nombre = getattr(self.usuario, 'nombre', 'Sistema')
        rol = getattr(self.usuario, 'rol', 'Administrador')
        depto = getattr(self.usuario, 'departamento', 'Operaciones')

        header_data = [[
            Paragraph(
                "<font size='15'><b>ESTADIO ANTONIO HERRERA GUTIÉRREZ</b></font>",
                self.style_bold
            ),
            Paragraph(
                f"<font size='8' color='#64748b'>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>",
                self.style_normal
            ),
        ], [
            Paragraph(
                f"<font size='9' color='#475569'>Departamento: <b>{depto}</b> | Rol: <b>{rol}</b></font>",
                self.style_normal
            ),
            Paragraph(
                f"<font size='9' color='#475569'>Generado por: <b>{usuario_nombre.upper()}</b></font>",
                self.style_normal
            ),
        ]]
        header_table = Table(header_data, colWidths=[360, 180])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 6))

        story.append(HRFlowable(
            width="100%", thickness=2,
            color=colors.HexColor('#1e40af'),
            spaceAfter=8
        ))
        story.append(Paragraph(self.TITULO, self.style_titulo))

        if filtros:
            orden = filtros.pop('orden', None)
            filtros_texto = ', '.join(
                f"{k}: {v}" for k, v in filtros.items() if v
            )
            if filtros_texto:
                story.append(Paragraph(
                    f"<font size='8' color='#64748b'><i>Filtros aplicados: {filtros_texto}</i></font>",
                    self.style_small
                ))
            if orden:
                story.append(Paragraph(
                    f"<font size='8' color='#64748b'><i>Ordenado por: {orden}</i></font>",
                    self.style_small
                ))
        story.append(Spacer(1, 8))
        return story

    def _tabla(self, datos, style_override=None, col_widths=None):
        story = []
        if not datos or len(datos) < 2:
            story.append(Paragraph(
                "<font color='#64748b'>No hay datos para mostrar.</font>",
                self.style_normal
            ))
            return story

        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        if style_override:
            table_style.extend(style_override)

        widths = col_widths or ([w for _, _, w in self.COLUMNAS] if self.COLUMNAS else None)
        table = Table(datos, colWidths=widths, repeatRows=1)
        table.setStyle(TableStyle(table_style))
        story.append(table)
        return story

    def generate(self, datos, filtros=None, kpis=None, opciones=None):
        buffer = io.BytesIO()
        opciones = opciones or {}
        analytics = opciones.get('analytics')

        columnas = self._obtener_columnas(opciones)
        orientacion = opciones.get('orientacion', 'vertical')
        pagina = self._determinar_pagina(columnas, orientacion)
        self._ajustar_estilo_segun_columnas(len(columnas))

        doc = SimpleDocTemplate(
            buffer, pagesize=pagina,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
        )

        story = []
        story.extend(self._header(filtros))

        if kpis:
            story.extend(self._seccion_kpis(kpis))

        story.extend(self._secciones_analisis(kpis, opciones))

        # Ordenamiento dinámico
        ordenar_por = opciones.get('ordenar_por')
        if ordenar_por:
            datos = sorted(datos, key=lambda x: x.get(ordenar_por) or '')

        # Tabla con columnas dinámicas o default
        col_ids = opciones.get('columnas_seleccionadas')
        if col_ids:
            agrupar_por = opciones.get('agrupar_por')
            if agrupar_por and any(c[1] == agrupar_por for c in columnas):
                table_data = self._construir_tabla_agrupada(datos, columnas, agrupar_por)
            else:
                table_data = self._construir_tabla_simple(datos, columnas)
        else:
            rows = self._build_rows(datos)
            if rows:
                header = [Paragraph(f"<b>{h}</b>", self.style_bold) for h, _, _ in self.COLUMNAS]
                table_data = [header] + rows
            else:
                table_data = None

        if table_data:
            anchos = self._calcular_anchos(columnas, orientacion) if col_ids else None
            story.extend(self._tabla(table_data, col_widths=anchos))
        else:
            story.append(Spacer(1, 20))
            story.append(Paragraph(
                "<font color='#64748b'>No hay datos para mostrar.</font>",
                self.style_normal
            ))

        # Hook para distribuciones (override en subclases)
        story.extend(self._post_table_sections(kpis, opciones))

        # Secciones de analítica (FASE 4E)
        if analytics:
            story.extend(self._seccion_analytics(analytics))

        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1')))
        story.append(Paragraph(
            f"<font size='7' color='#94a3b8'>Reporte generado automáticamente — "
            f"{self.TITULO} — {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>",
            self.style_small
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _build_rows(self, datos):
        return []

    def _secciones_analisis(self, kpis, opciones):
        """Resumen ejecutivo + Top-N + comparativa, según opciones del usuario."""
        story = []
        if not kpis:
            return story
        if opciones and opciones.get('resumen'):
            story.extend(self._resumen_ejecutivo(kpis))
        if opciones and opciones.get('top_n'):
            story.extend(self._top_destacados(kpis, opciones['top_n']))
        if opciones and opciones.get('comparar'):
            story.extend(self._comparativa_periodos(kpis, opciones.get('kpis_previos')))
        return story

    def _resumen_ejecutivo(self, kpis):
        """Párrafo factual: SOLO números ya calculados, cero texto inventado."""
        story = []
        if not kpis:
            return story

        def _fmt_val(k, v):
            if isinstance(v, float) and ('monto' in k or 'promedio' in k or 'costo' in k):
                return f"${v:,.0f}"
            if isinstance(v, int) and 'seg' in k:
                h, rem = divmod(v, 3600)
                m, s = divmod(rem, 60)
                return f"{h}h {m}m" if h else f"{m}m {s}s"
            if isinstance(v, float) and 'pct' in k:
                return f"{v}%"
            return str(v)

        partes = []
        total = None
        for clave in ('total', 'total_pagos', 'total_registros', 'modulos'):
            if isinstance(kpis.get(clave), (int, float)):
                total = kpis[clave]
                break
        if total is not None:
            partes.append(f"Se analizaron {total} registros tras aplicar los filtros seleccionados")
        detalles = []
        for k, v in kpis.items():
            if isinstance(v, (dict, list)) or v is None:
                continue
            if k in ('total', 'total_pagos', 'total_registros', 'modulos') or len(detalles) >= 3:
                continue
            detalles.append(f"{str(k).replace('_', ' ')}: {_fmt_val(k, v)}")
        if detalles:
            partes.append(' · '.join(detalles))
        if not partes:
            return story
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=4))
        story.append(Paragraph("<b>Resumen ejecutivo</b>", self.style_normal))
        story.append(Spacer(1, 2))
        story.append(Paragraph(
            f"<font size='9' color='#334155'>{'.'.join(partes)}.</font>",
            self.style_normal
        ))
        story.append(Spacer(1, 6))
        return story

    def _top_destacados(self, kpis, n):
        """Top N entidades por la distribución principal del módulo (reutiliza KPIs existentes)."""
        distribucion = next(
            (v for v in kpis.values() if isinstance(v, dict) and v), None
        )
        if not distribucion:
            return []
        ordenados = sorted(distribucion.items(), key=lambda x: x[1], reverse=True)[:max(int(n), 1)]
        return self._seccion_distribucion(f'Top {n} destacados', ordenados)

    def _comparativa_periodos(self, kpis, kpis_previos):
        """KPIs lado a lado vs el período anterior desplazado. Solo escalares compartidos."""
        story = []
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=4))
        story.append(Paragraph("<b>Comparativa vs período anterior</b>", self.style_normal))
        story.append(Spacer(1, 4))
        if not kpis_previos:
            story.append(Paragraph(
                "<font size='9' color='#64748b'><i>Sin datos comparables en el período anterior.</i></font>",
                self.style_normal
            ))
            story.append(Spacer(1, 6))
            return story
        rows = [[Paragraph('<b>Indicador</b>', self.style_bold),
                 Paragraph('<b>Actual</b>', self.style_bold),
                 Paragraph('<b>Anterior</b>', self.style_bold),
                 Paragraph('<b>Variación</b>', self.style_bold)]]
        comparados = 0
        for k, actual in kpis.items():
            if isinstance(actual, (dict, list)) or k not in kpis_previos:
                continue
            previo = kpis_previos[k]
            if isinstance(previo, (dict, list)):
                continue
            try:
                a, p = float(str(actual).replace('$', '').replace(',', '') or 0), \
                       float(str(previo).replace('$', '').replace(',', '') or 0)
            except (ValueError, TypeError):
                continue
            if p:
                variacion = f"{(a - p) / p * 100:+.0f}%"
            elif a:
                variacion = 'Nuevo'
            else:
                variacion = '—'
            rows.append([
                Paragraph(str(k).replace('_', ' ').title(), self.style_normal),
                Paragraph(str(actual), self.style_normal),
                Paragraph(str(previo), self.style_normal),
                Paragraph(variacion, self.style_normal),
            ])
            comparados += 1
        if not comparados:
            story.append(Paragraph(
                "<font size='9' color='#64748b'><i>Sin datos comparables en el período anterior.</i></font>",
                self.style_normal
            ))
            story.append(Spacer(1, 6))
            return story
        t = Table(rows, colWidths=[220, 110, 110, 90])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))
        return story

    def _seccion_kpis(self, kpis):
        story = []
        if not kpis:
            return story
        story.append(Spacer(1, 8))
        items = list(kpis.items())
        chunks = [items[i:i+3] for i in range(0, len(items), 3)]
        for chunk in chunks:
            row_cells = []
            for k, v in chunk:
                if isinstance(v, (dict, list)):
                    continue
                label = k.replace('_', ' ').title()
                texto = f"<font size='7' color='#64748b'>{label}</font><br/><font size='11'><b>{v}</b></font>"
                row_cells.append(Paragraph(texto, self.style_normal))
            if len(row_cells) < 3 and len(chunks) > 1:
                for _ in range(3 - len(row_cells)):
                    row_cells.append(Paragraph("", self.style_normal))
            if row_cells:
                w = 540 // len(row_cells) if row_cells else 180
                t = Table([row_cells], colWidths=[w]*len(row_cells))
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
                ]))
                story.append(t)
                story.append(Spacer(1, 4))
        story.append(Spacer(1, 8))
        return story

    def _seccion_distribucion(self, titulo, items, color=colors.HexColor('#1e40af')):
        story = []
        if not items:
            return story
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=4))
        story.append(Paragraph(
            f"<font size='9' color='#475569'><b>{titulo}</b></font>",
            self.style_normal
        ))
        story.append(Spacer(1, 4))
        total = sum(v for _, v in items)
        rows = []
        rows.append([Paragraph("<b>Item</b>", self.style_bold),
                     Paragraph("<b>Cantidad</b>", self.style_bold),
                     Paragraph("<b>%</b>", self.style_bold)])
        for name, val in items:
            pct = f"{val * 100 // total}%" if total else "0%"
            rows.append([
                Paragraph(str(name)[:30], self.style_normal),
                Paragraph(str(val), self.style_normal),
                Paragraph(pct, self.style_normal),
            ])
        rows.append([
            Paragraph("<b>Total</b>", self.style_bold),
            Paragraph(f"<b>{total}</b>", self.style_bold),
            Paragraph("<b>100%</b>", self.style_bold),
        ])
        t = Table(rows, colWidths=[250, 100, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), color),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('PADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-2), 0.3, colors.HexColor('#e2e8f0')),
            ('LINEBELOW', (0,-1), (-1,-1), 1, color),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t)
        story.append(Spacer(1, 8))
        return story

    def save(self, pdf_bytes, usuario_id, filtros=None):
        from app.model.reportes_model import ReporteModel

        now = datetime.now()
        fecha_path = now.strftime('%Y/%m')
        nombre_archivo = f"{self.MODULO}_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta_relativa = f"{fecha_path}/{nombre_archivo}"
        ruta_completa = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'static', 'reportes', ruta_relativa
        )

        os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
        with open(ruta_completa, 'wb') as f:
            f.write(pdf_bytes)

        ReporteModel().registrar({
            'usuario_id': usuario_id,
            'modulo': self.MODULO,
            'tipo_reporte': self.TITULO,
            'filtros': filtros or {},
            'archivo_ruta': ruta_relativa,
            'archivo_nombre': f"{self.MODULO}_{now.strftime('%d-%m-%Y')}.pdf",
            'archivo_tamano': len(pdf_bytes),
        })

        return ruta_relativa, nombre_archivo
