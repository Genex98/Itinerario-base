"""
Analítica específica por módulo.

Cada función recibe los datos normalizados de reportes_data.py
y produce un AnalyticsResult usando los motores reutilizables.
"""

from datetime import datetime, timedelta
from .reportes_analytics import (
    AnalyticsResult, Severity,
    safe_count, safe_sum, safe_average, safe_min, safe_max,
    safe_percentage, safe_ratio,
    compute_trend, compute_ranking, compute_distribution, compare_periods,
    eval_date_expired, eval_date_expiring, eval_age_above,
    eval_count_above, eval_concentration, eval_field_threshold,
    eval_or, deduplicate_alerts, _parse_date,
)


# ============================================================
# MÓDULO 1 — CONTRATOS
# ============================================================

def analytics_contratos(records, kpis=None, today=None):
    result = AnalyticsResult('contratos')
    if not records:
        return result

    now = today or datetime.now()

    total = safe_count(records)
    vigentes = sum(1 for r in records if r.get('estatus') == 'Vigente')
    vencidos = sum(1 for r in records if r.get('estatus') == 'Vencido')
    borradores = sum(1 for r in records if r.get('estatus') == 'Borrador')

    montos = [float(r.get('monto_total', 0)) for r in records if r.get('monto_total') is not None]
    monto_total = sum(montos) if montos else 0
    monto_avg = monto_total / len(montos) if montos else 0
    monto_min = min(montos) if montos else 0
    monto_max = max(montos) if montos else 0

    monto_vigentes = sum(float(r.get('monto_total', 0)) for r in records
                         if r.get('estatus') == 'Vigente' and r.get('monto_total') is not None)

    result.add_metric('total', 'Total contratos', total, 'count',
                      source_fields=['estatus'])
    result.add_metric('vigentes', 'Vigentes', vigentes, 'count',
                      source_fields=['estatus'])
    result.add_metric('vencidos', 'Vencidos', vencidos, 'count',
                      source_fields=['estatus'])
    result.add_metric('borradores', 'Borradores', borradores, 'count',
                      source_fields=['estatus'])
    result.add_metric('vigentes_pct', 'Porcentaje vigentes',
                      round(safe_percentage(vigentes, total), 1), 'percent',
                      formula='vigentes / total * 100',
                      source_fields=['estatus'], precision=1)
    result.add_metric('monto_total', 'Monto total', round(monto_total, 2), 'currency',
                      formula='SUM(monto_total)',
                      source_fields=['monto_total'])
    result.add_metric('monto_promedio', 'Monto promedio', round(monto_avg, 2), 'currency',
                      formula='AVG(monto_total)',
                      source_fields=['monto_total'])
    result.add_metric('monto_min', 'Monto mínimo', round(monto_min, 2), 'currency',
                      source_fields=['monto_total'])
    result.add_metric('monto_max', 'Monto máximo', round(monto_max, 2), 'currency',
                      source_fields=['monto_total'])
    result.add_metric('monto_vigentes', 'Monto vigentes', round(monto_vigentes, 2), 'currency',
                      source_fields=['monto_total', 'estatus'])

    result.add_distribution('dist_tipo', 'Distribución por tipo',
                            compute_distribution(records, 'tipo').items, total)
    result.add_distribution('dist_estatus', 'Distribución por estatus',
                            compute_distribution(records, 'estatus').items, total)
    result.add_distribution('dist_patrocinador', 'Distribución por patrocinador',
                            compute_distribution(records, 'nombre_empresa').items, total)

    result.add_ranking('rank_monto', 'Top patrocinadores por monto',
                       compute_ranking(records, 'nombre_empresa', 'monto_total',
                                       aggregation='sum', top_n=5).items)

    result.add_trend('trend_por_inicio', 'Contratos por mes de inicio',
                     compute_trend(records, 'fecha_inicio', aggregation='count',
                                   granularity='month').data)

    if kpis and 'kpis_previos' in kpis:
        prev = kpis['kpis_previos']
        for key in ['total', 'vigentes', 'vencidos', 'monto_total']:
            if key in prev:
                result.add_comparison(key, result.metrics[0].value if key == 'total'
                                      else next((m.value for m in result.metrics if m.key == key), 0),
                                      prev[key])

    hoy = now.date() if isinstance(now, datetime) else now
    vencidos_registros = []
    por_vencer_7 = []
    por_vencer_30 = []
    por_vencer_60 = []
    por_vencer_90 = []
    for r in records:
        df = r.get('dias_restantes')
        if df is None or df == '—':
            continue
        try:
            dias = int(df)
        except (TypeError, ValueError):
            continue
        if dias < 0:
            vencidos_registros.append(r)
        elif dias <= 7:
            por_vencer_7.append(r)
        elif dias <= 30:
            por_vencer_30.append(r)
        elif dias <= 60:
            por_vencer_60.append(r)
        elif dias <= 90:
            por_vencer_90.append(r)

    if vencidos_registros:
        result.add_alert('contratos_vencidos', 'contratos', Severity.CRITICAL,
                         'Contratos vencidos',
                         f'{len(vencidos_registros)} contratos han superado su fecha de fin',
                         len(vencidos_registros),
                         evidence={'affected_count': len(vencidos_registros),
                                   'sample_records': [{'nombre_empresa': r.get('nombre_empresa'),
                                                       'dias_restantes': r.get('dias_restantes')}
                                                      for r in vencidos_registros[:10]]})
    if por_vencer_7:
        result.add_alert('contratos_vencer_7d', 'contratos', Severity.CRITICAL,
                         'Vencen en 7 días',
                         f'{len(por_vencer_7)} contratos vencen en 7 días o menos',
                         len(por_vencer_7),
                         evidence={'affected_count': len(por_vencer_7),
                                   'sample_records': [{'nombre_empresa': r.get('nombre_empresa'),
                                                       'dias_restantes': r.get('dias_restantes')}
                                                      for r in por_vencer_7[:10]]})
    if por_vencer_30:
        result.add_alert('contratos_vencer_30d', 'contratos', Severity.WARNING,
                         'Vencen en 30 días',
                         f'{len(por_vencer_30)} contratos vencen en 30 días o menos',
                         len(por_vencer_30),
                         evidence={'affected_count': len(por_vencer_30)})
    if por_vencer_60:
        result.add_alert('contratos_vencer_60d', 'contratos', Severity.WARNING,
                         'Vencen en 60 días',
                         f'{len(por_vencer_60)} contratos vencen en 60 días',
                         len(por_vencer_60))
    if por_vencer_90:
        result.add_alert('contratos_vencer_90d', 'contratos', Severity.INFO,
                         'Vencen en 90 días',
                         f'{len(por_vencer_90)} contratos vencen en 90 días',
                         len(por_vencer_90))

    groups = {}
    for r in records:
        emp = r.get('nombre_empresa', '—')
        groups.setdefault(emp, 0)
        try:
            groups[emp] += float(r.get('monto_total', 0))
        except (TypeError, ValueError):
            pass
    if groups and total >= 3:
        sorted_g = sorted(groups.items(), key=lambda x: x[1], reverse=True)
        top3_sum = sum(v for _, v in sorted_g[:3])
        top3_pct = safe_percentage(top3_sum, monto_total)
        if top3_pct > 60:
            result.add_insight('conc_monto_top3',
                               f'Los 3 principales patrocinadores concentran el {top3_pct:.0f}% del monto total.',
                               Severity.INFO)

    return result


# ============================================================
# MÓDULO 2 — BALANCE / PAGOS
# ============================================================

def analytics_balance(records, kpis=None, today=None):
    result = AnalyticsResult('balance')
    if not records:
        return result

    total = safe_count(records)
    monto_total = safe_sum(records, 'monto')
    monto_avg = safe_average(records, 'monto')
    monto_min = safe_min(records, 'monto') or 0
    monto_max = safe_max(records, 'monto') or 0

    result.add_metric('total_pagos', 'Total pagos', total, 'count',
                      source_fields=['id_pago'])
    result.add_metric('monto_total', 'Monto total', round(monto_total, 2), 'currency',
                      formula='SUM(monto)', source_fields=['monto'])
    result.add_metric('monto_promedio', 'Monto promedio', round(monto_avg, 2), 'currency',
                      formula='AVG(monto)', source_fields=['monto'])
    result.add_metric('monto_min', 'Monto mínimo', round(monto_min, 2), 'currency',
                      source_fields=['monto'])
    result.add_metric('monto_max', 'Monto máximo', round(monto_max, 2), 'currency',
                      source_fields=['monto'])

    result.add_distribution('dist_tipo_pago', 'Distribución por tipo de pago',
                            compute_distribution(records, 'tipo_pago').items, total)
    result.add_distribution('dist_patrocinador', 'Distribución por patrocinador',
                            compute_distribution(records, 'nombre_patrocinador').items, total)

    result.add_ranking('rank_patrocinador', 'Top patrocinadores por monto',
                       compute_ranking(records, 'nombre_patrocinador', 'monto',
                                       aggregation='sum', top_n=5).items)
    result.add_ranking('rank_contrato', 'Contratos con más pagos',
                       compute_ranking(records, 'id_contrato', aggregation='count',
                                       top_n=5).items)

    result.add_trend('trend_por_pago', 'Pagos por mes',
                     compute_trend(records, 'fecha_pago', aggregation='count',
                                   granularity='month').data)
    result.add_trend('trend_monto_por_pago', 'Monto por mes',
                     compute_trend(records, 'fecha_pago', 'monto', aggregation='sum',
                                   granularity='month').data)

    if total > 0:
        groups = {}
        for r in records:
            emp = r.get('nombre_patrocinador', '—')
            groups.setdefault(emp, 0)
            try:
                groups[emp] += float(r.get('monto', 0))
            except (TypeError, ValueError):
                pass
        if groups:
            sorted_g = sorted(groups.items(), key=lambda x: x[1], reverse=True)
            top1_pct = safe_percentage(sorted_g[0][1], monto_total) if sorted_g else 0
            if top1_pct > 40:
                result.add_insight('conc_pago_top1',
                                   f'El patrocinador "{sorted_g[0][0]}" concentra el {top1_pct:.0f}% del monto total.',
                                   Severity.INFO)

    return result


# ============================================================
# MÓDULO 3 — PATROCINADORES
# ============================================================

def analytics_patrocinadores(records, kpis=None, today=None):
    result = AnalyticsResult('patrocinadores')
    if not records:
        return result

    total = safe_count(records)
    activos = sum(1 for r in records if r.get('estado') == 1 or r.get('estado') == '1')
    inactivos = total - activos

    result.add_metric('total', 'Total patrocinadores', total, 'count',
                      source_fields=['id'])
    result.add_metric('activos', 'Activos', activos, 'count',
                      source_fields=['estado'])
    result.add_metric('inactivos', 'Inactivos', inactivos, 'count',
                      source_fields=['estado'])
    result.add_metric('activos_pct', 'Porcentaje activos',
                      round(safe_percentage(activos, total), 1), 'percent',
                      formula='activos / total * 100', precision=1)

    result.add_distribution('dist_tipo', 'Distribución por tipo de contrato',
                            compute_distribution(records, 'tipo_contrato').items, total)

    result.add_trend('trend_tipo', 'Distribución por tipo',
                     compute_trend(records, 'tipo_contrato', aggregation='count',
                                   granularity='month').data)

    return result


# ============================================================
# MÓDULO 4 — MANTENIMIENTO
# ============================================================

def analytics_mantenimiento(records, kpis=None, today=None):
    result = AnalyticsResult('mantenimiento')
    if not records:
        return result

    total = safe_count(records)
    en_espera = sum(1 for r in records if r.get('estado') == 'en_espera')
    en_reparacion = sum(1 for r in records if r.get('estado') == 'en_reparacion')
    reparados = sum(1 for r in records if r.get('estado') == 'reparado')
    dados_baja = sum(1 for r in records if r.get('estado') == 'baja')

    dias_vals = []
    for r in records:
        d = r.get('dias_en_taller')
        if d is not None:
            try:
                dias_vals.append(float(d))
            except (TypeError, ValueError):
                pass

    promedio_dias = sum(dias_vals) / len(dias_vals) if dias_vals else 0
    max_dias = max(dias_vals) if dias_vals else 0
    min_dias = min(dias_vals) if dias_vals else 0

    result.add_metric('total', 'Total mantenimientos', total, 'count',
                      source_fields=['id'])
    result.add_metric('en_espera', 'En espera', en_espera, 'count',
                      source_fields=['estado'])
    result.add_metric('en_reparacion', 'En reparación', en_reparacion, 'count',
                      source_fields=['estado'])
    result.add_metric('reparados', 'Reparados', reparados, 'count',
                      source_fields=['estado'])
    result.add_metric('dados_baja', 'Dados de baja', dados_baja, 'count',
                      source_fields=['estado'])
    result.add_metric('promedio_dias', 'Promedio días en taller',
                      round(promedio_dias, 1), 'days',
                      formula='AVG(dias_en_taller)', precision=1)
    result.add_metric('max_dias', 'Máximo días en taller',
                      round(max_dias, 1), 'days', precision=1)
    result.add_metric('min_dias', 'Mínimo días en taller',
                      round(min_dias, 1), 'days', precision=1)

    result.add_distribution('dist_estado', 'Distribución por estado',
                            compute_distribution(records, 'estado').items, total)
    result.add_distribution('dist_recurso', 'Recursos más afectados',
                            compute_distribution(records, 'recurso_nombre').items, total)

    result.add_ranking('rank_recursos', 'Recursos con más mantenimientos',
                       compute_ranking(records, 'recurso_nombre', aggregation='count',
                                       top_n=5).items)
    result.add_ranking('rank_dias', 'Recursos con más días en taller',
                       compute_ranking(records, 'recurso_nombre', 'dias_en_taller',
                                       aggregation='sum', top_n=5).items)

    result.add_trend('trend_por_ingreso', 'Mantenimientos por mes',
                     compute_trend(records, 'fecha_ingreso', aggregation='count',
                                   granularity='month').data)

    now = today or datetime.now()
    largos = [r for r in records
              if r.get('estado') in ('en_espera', 'en_reparacion') and r.get('dias_en_taller') is not None]
    largos_filtrados = []
    for r in largos:
        try:
            if int(r['dias_en_taller']) > 14:
                largos_filtrados.append(r)
        except (TypeError, ValueError):
            pass
    if largos_filtrados:
        result.add_alert('mantenimiento_prolongado', 'mantenimiento', Severity.WARNING,
                         'Mantenimiento prolongado',
                         f'{len(largos_filtrados)} recursos llevan más de 14 días en taller',
                         len(largos_filtrados),
                         evidence={'affected_count': len(largos_filtrados),
                                   'sample_records': [{'recurso_nombre': r.get('recurso_nombre'),
                                                       'dias_en_taller': r.get('dias_en_taller'),
                                                       'estado': r.get('estado')}
                                                      for r in largos_filtrados[:10]]})

    return result


# ============================================================
# MÓDULO 5 — TAREAS
# ============================================================

def analytics_tareas(records, kpis=None, today=None):
    result = AnalyticsResult('tareas')
    if not records:
        return result

    total = safe_count(records)
    pendientes = sum(1 for r in records if r.get('estado') == 'Pendiente')
    en_progreso = sum(1 for r in records if r.get('estado') == 'En Progreso')
    completadas = sum(1 for r in records if r.get('estado') == 'Completada')
    pct_completado = safe_percentage(completadas, total)

    result.add_metric('total', 'Total tareas', total, 'count',
                      source_fields=['id_tarea'])
    result.add_metric('pendientes', 'Pendientes', pendientes, 'count',
                      source_fields=['estado'])
    result.add_metric('en_progreso', 'En progreso', en_progreso, 'count',
                      source_fields=['estado'])
    result.add_metric('completadas', 'Completadas', completadas, 'count',
                      source_fields=['estado'])
    result.add_metric('completadas_pct', 'Porcentaje completado',
                      round(pct_completado, 1), 'percent',
                      formula='completadas / total * 100', precision=1)

    result.add_distribution('dist_estado', 'Distribución por estado',
                            compute_distribution(records, 'estado').items, total)
    result.add_distribution('dist_responsable', 'Distribución por responsable',
                            compute_distribution(records, 'asignado_a').items, total)

    result.add_ranking('rank_responsable', 'Responsables con más tareas pendientes',
                       compute_ranking([r for r in records if r.get('estado') == 'Pendiente'],
                                       'asignado_a', aggregation='count', top_n=5).items)

    result.add_trend('trend_asignaciones', 'Asignaciones por mes',
                     compute_trend(records, 'fecha_asignacion_tarea', aggregation='count',
                                   granularity='month').data)

    now = today or datetime.now()
    antiguas = []
    for r in records:
        if r.get('estado') != 'Pendiente':
            continue
        fa = r.get('fecha_asignacion_tarea')
        if not fa:
            continue
        dt = _parse_date(fa)
        if dt is None:
            continue
        dias = (now - dt).days if isinstance(now, datetime) else (now - dt.date()).days
        if dias > 14:
            antiguas.append({**r, '_age_days': dias})

    if antiguas:
        result.add_alert('tareas_antiguas', 'tareas', Severity.WARNING,
                         'Tareas pendientes antiguas',
                         f'{len(antiguas)} tareas pendientes con más de 14 días',
                         len(antiguas),
                         evidence={'affected_count': len(antiguas),
                                   'sample_records': [{'nombre_tarea': r.get('nombre_tarea'),
                                                       'asignado_a': r.get('asignado_a'),
                                                       '_age_days': r.get('_age_days')}
                                                      for r in antiguas[:10]]})

    return result


# ============================================================
# MÓDULO 6 — PREMIOS
# ============================================================

def analytics_premios(records, kpis=None, today=None):
    result = AnalyticsResult('premios')
    if not records:
        return result

    total = safe_count(records)
    total_cantidad = sum(int(r.get('cantidad', 0)) for r in records
                         if r.get('cantidad') is not None)
    total_entregada = sum(int(r.get('cantidad_entregada', 0)) for r in records
                          if r.get('cantidad_entregada') is not None)
    pendientes = sum(1 for r in records if r.get('estado') == 'pendiente')
    entregados = sum(1 for r in records if r.get('estado') == 'entregado')
    tasa_entrega = safe_percentage(total_entregada, total_cantidad)
    brecha = total_cantidad - total_entregada

    result.add_metric('total', 'Total premios', total, 'count',
                      source_fields=['id'])
    result.add_metric('total_cantidad', 'Cantidad total', total_cantidad, 'count',
                      formula='SUM(cantidad)', source_fields=['cantidad'])
    result.add_metric('total_entregada', 'Cantidad entregada', total_entregada, 'count',
                      formula='SUM(cantidad_entregada)', source_fields=['cantidad_entregada'])
    result.add_metric('pendientes', 'Premios pendientes', pendientes, 'count',
                      source_fields=['estado'])
    result.add_metric('entregados', 'Premios entregados', entregados, 'count',
                      source_fields=['estado'])
    result.add_metric('tasa_entrega', 'Tasa de entrega',
                      round(tasa_entrega, 1), 'percent',
                      formula='total_entregada / total_cantidad * 100', precision=1)
    result.add_metric('brecha', 'Brecha pendiente', brecha, 'count',
                      formula='total_cantidad - total_entregada')

    result.add_distribution('dist_estado', 'Distribución por estado',
                            compute_distribution(records, 'estado').items, total)
    result.add_distribution('dist_patrocinador', 'Distribución por patrocinador',
                            compute_distribution(records, 'patrocinador_nombre').items, total)

    result.add_ranking('rank_patrocinador', 'Top patrocinadores por cantidad',
                       compute_ranking(records, 'patrocinador_nombre', aggregation='count',
                                       top_n=5).items)

    result.add_trend('trend_creaciones', 'Premios creados por mes',
                     compute_trend(records, 'fecha_creacion', aggregation='count',
                                   granularity='month').data)

    if total_cantidad > 0 and tasa_entrega < 50:
        result.add_insight('baja_entrega',
                           f'La tasa de entrega es del {tasa_entrega:.0f}%, menor al 50%.',
                           Severity.WARNING)

    return result


# ============================================================
# MÓDULO 7 — INVENTARIO
# ============================================================

def analytics_inventario(records, kpis=None, today=None):
    result = AnalyticsResult('inventario')
    if not records:
        return result

    total = safe_count(records)
    costo_total = safe_sum(records, 'costo')
    costo_avg = safe_average(records, 'costo')
    costo_min = safe_min(records, 'costo') or 0
    costo_max = safe_max(records, 'costo') or 0

    result.add_metric('total', 'Total recursos', total, 'count',
                      source_fields=['id'])
    result.add_metric('costo_total', 'Valor total', round(costo_total, 2), 'currency',
                      formula='SUM(costo)', source_fields=['costo'])
    result.add_metric('costo_promedio', 'Costo promedio', round(costo_avg, 2), 'currency',
                      formula='AVG(costo)', source_fields=['costo'])
    result.add_metric('costo_min', 'Costo mínimo', round(costo_min, 2), 'currency',
                      source_fields=['costo'])
    result.add_metric('costo_max', 'Costo máximo', round(costo_max, 2), 'currency',
                      source_fields=['costo'])

    result.add_distribution('dist_tipo', 'Distribución por tipo',
                            compute_distribution(records, 'tipo_nombre').items, total)
    result.add_distribution('dist_estado', 'Distribución por estado',
                            compute_distribution(records, 'estado_nombre').items, total)

    tipo_groups = {}
    for r in records:
        t = r.get('tipo_nombre', '—')
        tipo_groups.setdefault(t, 0)
        try:
            tipo_groups[t] += float(r.get('costo', 0))
        except (TypeError, ValueError):
            pass
    if tipo_groups:
        result.add_ranking('rank_valor_tipo', 'Tipos por valor total',
                           [__import__('app.helpers.reportes_analytics', fromlist=['RankingItem']).RankingItem(
                               item=k, value=round(v, 2), position=i + 1)
                            for i, (k, v) in enumerate(sorted(tipo_groups.items(),
                                                              key=lambda x: x[1], reverse=True)[:5])])

    result.add_trend('trend_adquisiciones', 'Adquisiciones por mes',
                     compute_trend(records, 'fecha_compra', aggregation='count',
                                   granularity='month').data)
    result.add_trend('trend_inversion', 'Inversión por mes',
                     compute_trend(records, 'fecha_compra', 'costo', aggregation='sum',
                                   granularity='month').data)

    return result


# ============================================================
# MÓDULO 8 — GUIONES
# ============================================================

def analytics_guiones(records, kpis=None, today=None):
    result = AnalyticsResult('guiones')
    if not records:
        return result

    total = safe_count(records)
    borradores = sum(1 for r in records if r.get('estado') == 'borrador')
    publicados = sum(1 for r in records if r.get('estado') == 'publicado')
    en_vivo = sum(1 for r in records if r.get('estado') == 'en_vivo')
    finalizados = sum(1 for r in records if r.get('estado') == 'finalizado')

    tiempos = [float(r.get('tiempo_segundos', 0)) for r in records
               if r.get('tiempo_segundos') is not None]
    tiempo_total = sum(tiempos) if tiempos else 0
    tiempo_promedio = tiempo_total / len(tiempos) if tiempos else 0
    tiempo_min = min(tiempos) if tiempos else 0
    tiempo_max = max(tiempos) if tiempos else 0

    total_game = sum(int(r.get('game', 0)) for r in records
                     if r.get('game') is not None)
    total_pregame = sum(int(r.get('pregame', 0)) for r in records
                        if r.get('pregame') is not None)

    result.add_metric('total', 'Total guiones', total, 'count',
                      source_fields=['id'])
    result.add_metric('borradores', 'Borradores', borradores, 'count',
                      source_fields=['estado'])
    result.add_metric('publicados', 'Publicados', publicados, 'count',
                      source_fields=['estado'])
    result.add_metric('en_vivo', 'En vivo', en_vivo, 'count',
                      source_fields=['estado'])
    result.add_metric('finalizados', 'Finalizados', finalizados, 'count',
                      source_fields=['estado'])
    result.add_metric('tiempo_total', 'Tiempo total programado', round(tiempo_total, 0), 'seconds',
                      formula='SUM(tiempo_segundos)', source_fields=['tiempo_segundos'])
    result.add_metric('tiempo_promedio', 'Duración promedio', round(tiempo_promedio, 0), 'seconds',
                      formula='AVG(tiempo_segundos)', source_fields=['tiempo_segundos'])
    result.add_metric('tiempo_min', 'Duración mínima', round(tiempo_min, 0), 'seconds',
                      source_fields=['tiempo_segundos'])
    result.add_metric('tiempo_max', 'Duración máxima', round(tiempo_max, 0), 'seconds',
                      source_fields=['tiempo_segundos'])
    result.add_metric('total_game', 'Elementos Game', total_game, 'count',
                      source_fields=['game'])
    result.add_metric('total_pregame', 'Elementos Pregame', total_pregame, 'count',
                      source_fields=['pregame'])

    result.add_distribution('dist_estado', 'Distribución por estado',
                            compute_distribution(records, 'estado').items, total)

    result.add_trend('trend_creaciones', 'Guiones creados por mes',
                     compute_trend(records, 'creado_en', aggregation='count',
                                   granularity='month').data)

    return result


# ============================================================
# MÓDULO 9 — BITÁCORA
# ============================================================

def analytics_bitacora(records, kpis=None, today=None):
    result = AnalyticsResult('bitacora')
    if not records:
        return result

    total = safe_count(records)
    creaciones = sum(1 for r in records if r.get('tipo_accion') == 'create')
    ediciones = sum(1 for r in records if r.get('tipo_accion') == 'update')
    eliminaciones = sum(1 for r in records if r.get('tipo_accion') == 'delete')

    result.add_metric('total', 'Total acciones', total, 'count',
                      source_fields=['id'])
    result.add_metric('creaciones', 'Creaciones', creaciones, 'count',
                      source_fields=['tipo_accion'])
    result.add_metric('ediciones', 'Ediciones', ediciones, 'count',
                      source_fields=['tipo_accion'])
    result.add_metric('eliminaciones', 'Eliminaciones', eliminaciones, 'count',
                      source_fields=['tipo_accion'])

    result.add_distribution('dist_tipo_accion', 'Distribución por tipo de acción',
                            compute_distribution(records, 'tipo_accion').items, total)
    result.add_distribution('dist_modulo', 'Actividad por módulo',
                            compute_distribution(records, 'modulo').items, total)
    result.add_distribution('dist_usuario', 'Actividad por usuario',
                            compute_distribution(records, 'usuario_nombre').items, total)

    result.add_ranking('rank_usuarios', 'Top usuarios por actividad',
                       compute_ranking(records, 'usuario_nombre', aggregation='count',
                                       top_n=5).items)
    result.add_ranking('rank_modulos', 'Módulos más utilizados',
                       compute_ranking(records, 'modulo', aggregation='count',
                                       top_n=5).items)

    result.add_trend('trend_actividad', 'Actividad por mes',
                     compute_trend(records, 'created_at', aggregation='count',
                                   granularity='month').data)

    if total > 0:
        mod_counts = {}
        for r in records:
            m = r.get('modulo', '—')
            mod_counts[m] = mod_counts.get(m, 0) + 1
        if mod_counts:
            top_mod = max(mod_counts.items(), key=lambda x: x[1])
            top_pct = safe_percentage(top_mod[1], total)
            if top_pct > 50:
                result.add_insight('mod_dominante',
                                   f'El módulo "{top_mod[0]}" concentra el {top_pct:.0f}% de la actividad.',
                                   Severity.INFO)

    return result


# ============================================================
# MÓDULO 10 — USUARIOS
# ============================================================

def analytics_usuarios(records, kpis=None, today=None):
    result = AnalyticsResult('usuarios')
    if not records:
        return result

    total = safe_count(records)
    activos = sum(1 for r in records if r.get('activo') == 1 or r.get('activo') == '1')
    inactivos = total - activos

    result.add_metric('total', 'Total usuarios', total, 'count',
                      source_fields=['id'])
    result.add_metric('activos', 'Activos', activos, 'count',
                      source_fields=['activo'])
    result.add_metric('inactivos', 'Inactivos', inactivos, 'count',
                      source_fields=['activo'])
    result.add_metric('activos_pct', 'Porcentaje activos',
                      round(safe_percentage(activos, total), 1), 'percent',
                      formula='activos / total * 100', precision=1)

    result.add_distribution('dist_rol', 'Distribución por rol',
                            compute_distribution(records, 'rol').items, total)
    result.add_distribution('dist_departamento', 'Distribución por departamento',
                            compute_distribution(records, 'departamento').items, total)

    result.add_trend('trend_registros', 'Registros por mes',
                     compute_trend(records, 'fecha_registro', aggregation='count',
                                   granularity='month').data)

    return result


# ============================================================
# MÓDULO 11 — REELS
# ============================================================

def analytics_reels(records, kpis=None, today=None):
    result = AnalyticsResult('reels')
    if not records:
        return result

    total = safe_count(records)
    total_videos = sum(int(r.get('videos_count', 0)) for r in records
                       if r.get('videos_count') is not None)

    duraciones = [float(r.get('duracion_total', 0)) for r in records
                  if r.get('duracion_total') is not None]
    duracion_total_min = sum(duraciones) if duraciones else 0
    duracion_total_seg = duracion_total_min * 60
    duracion_promedio_seg = (duracion_total_seg / len(duraciones)) if duraciones else 0

    result.add_metric('total', 'Total reels', total, 'count',
                      source_fields=['id'])
    result.add_metric('total_videos', 'Total videos', total_videos, 'count',
                      source_fields=['videos_count'])
    result.add_metric('duracion_total', 'Duración total',
                      round(duracion_total_seg, 0), 'seconds',
                      formula='SUM(duracion_total * 60)', source_fields=['duracion_total'])
    result.add_metric('duracion_promedio', 'Duración promedio',
                      round(duracion_promedio_seg, 0), 'seconds',
                      formula='AVG(duracion_total * 60)', source_fields=['duracion_total'])
    result.add_metric('videos_por_reel', 'Videos por reel promedio',
                      round(safe_ratio(total_videos, total), 1), 'decimal', precision=1)

    result.add_distribution('dist_patrocinador', 'Distribución por patrocinador',
                            compute_distribution(records, 'patrocinado').items, total)

    result.add_ranking('rank_patrocinador', 'Top patrocinadores por reels',
                       compute_ranking(records, 'patrocinado', aggregation='count',
                                       top_n=5).items)

    result.add_trend('trend_creaciones', 'Reels creados por mes',
                     compute_trend(records, 'creado_en', aggregation='count',
                                   granularity='month').data)

    return result


# ============================================================
# REGISTRO CENTRAL
# ============================================================

ANALYTICS_FUNCTIONS = {
    'contratos': analytics_contratos,
    'balance': analytics_balance,
    'patrocinadores': analytics_patrocinadores,
    'mantenimiento': analytics_mantenimiento,
    'tareas': analytics_tareas,
    'premios': analytics_premios,
    'inventario': analytics_inventario,
    'guiones': analytics_guiones,
    'bitacora': analytics_bitacora,
    'usuarios': analytics_usuarios,
    'reels': analytics_reels,
}


def run_analytics(modulo, records, kpis=None, today=None):
    fn = ANALYTICS_FUNCTIONS.get(modulo)
    if not fn:
        return AnalyticsResult(modulo)
    return fn(records, kpis=kpis, today=today)
