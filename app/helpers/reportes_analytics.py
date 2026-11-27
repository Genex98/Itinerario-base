"""
Motores analíticos reutilizables para el sistema de reportes.

Separación DATA/ANALYTICS/PRESENTATION:
- Este módulo produce estructuras de datos tipadas.
- NO genera HTML, PDF, ni formatea para display.
- Valores numéricos se mantienen como int/float/Decimal.
"""

from datetime import datetime, timedelta, date as _date
from enum import Enum
from calendar import monthrange


# ============================================================
# CONTRATOS DE DATOS
# ============================================================

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    UNCHANGED = "unchanged"
    NOT_COMPARABLE = "not_comparable"


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Metric:
    __slots__ = ('key', 'label', 'formula', 'source_fields', 'value', 'unit', 'precision')

    def __init__(self, key, label, value, unit='count', formula='', source_fields=None, precision=0):
        self.key = key
        self.label = label
        self.formula = formula
        self.source_fields = source_fields or []
        self.value = value
        self.unit = unit
        self.precision = precision

    def to_dict(self):
        return {
            'key': self.key, 'label': self.label, 'formula': self.formula,
            'source_fields': self.source_fields, 'value': self.value,
            'unit': self.unit, 'precision': self.precision,
        }


class DistributionItem:
    __slots__ = ('category', 'count', 'percentage')

    def __init__(self, category, count, percentage):
        self.category = category
        self.count = count
        self.percentage = percentage

    def to_dict(self):
        return {'category': self.category, 'count': self.count, 'percentage': self.percentage}


class Distribution:
    __slots__ = ('key', 'label', 'items', 'total')

    def __init__(self, key, label, items, total):
        self.key = key
        self.label = label
        self.items = items
        self.total = total

    def to_dict(self):
        return {
            'key': self.key, 'label': self.label,
            'items': [i.to_dict() for i in self.items], 'total': self.total,
        }


class TrendPoint:
    __slots__ = ('period', 'value', 'previous_value', 'absolute_change', 'percentage_change')

    def __init__(self, period, value, previous_value=None, absolute_change=None, percentage_change=None):
        self.period = period
        self.value = value
        self.previous_value = previous_value
        self.absolute_change = absolute_change
        self.percentage_change = percentage_change

    def to_dict(self):
        return {
            'period': self.period, 'value': self.value,
            'previous_value': self.previous_value,
            'absolute_change': self.absolute_change,
            'percentage_change': self.percentage_change,
        }


class Trend:
    __slots__ = ('key', 'label', 'data')

    def __init__(self, key, label, data):
        self.key = key
        self.label = label
        self.data = data

    def to_dict(self):
        return {'key': self.key, 'label': self.label, 'data': [p.to_dict() for p in self.data]}


class RankingItem:
    __slots__ = ('item', 'value', 'position')

    def __init__(self, item, value, position):
        self.item = item
        self.value = value
        self.position = position

    def to_dict(self):
        return {'item': self.item, 'value': self.value, 'position': self.position}


class Ranking:
    __slots__ = ('key', 'label', 'items')

    def __init__(self, key, label, items):
        self.key = key
        self.label = label
        self.items = items

    def to_dict(self):
        return {'key': self.key, 'label': self.label, 'items': [i.to_dict() for i in self.items]}


class Comparison:
    __slots__ = ('indicator', 'current', 'previous', 'absolute_change', 'percentage_change', 'direction')

    def __init__(self, indicator, current, previous, absolute_change, percentage_change, direction):
        self.indicator = indicator
        self.current = current
        self.previous = previous
        self.absolute_change = absolute_change
        self.percentage_change = percentage_change
        self.direction = direction

    def to_dict(self):
        return {
            'indicator': self.indicator, 'current': self.current,
            'previous': self.previous, 'absolute_change': self.absolute_change,
            'percentage_change': self.percentage_change, 'direction': self.direction.value,
        }


class Alert:
    __slots__ = ('id', 'module', 'rule', 'severity', 'title', 'description',
                 'value', 'threshold', 'unit', 'affected_count', 'evidence', 'data')

    def __init__(self, id, module, severity, title, description, count=0, data=None,
                 rule='', value=None, threshold=None, unit='', affected_count=0, evidence=None):
        self.id = id
        self.module = module
        self.rule = rule
        self.severity = severity
        self.title = title
        self.description = description
        self.value = value if value is not None else count
        self.threshold = threshold
        self.unit = unit
        self.affected_count = affected_count if affected_count else count
        self.evidence = evidence
        self.data = data or []

    def to_dict(self):
        d = {
            'id': self.id, 'module': self.module, 'rule': self.rule,
            'severity': self.severity.value if hasattr(self.severity, 'value') else self.severity,
            'title': self.title, 'description': self.description,
            'value': self.value, 'threshold': self.threshold, 'unit': self.unit,
            'affected_count': self.affected_count,
        }
        if self.evidence:
            d['evidence'] = self.evidence.to_dict()
        if self.data:
            d['data'] = self.data
        return d


class Insight:
    __slots__ = ('key', 'text', 'severity')

    def __init__(self, key, text, severity=Severity.INFO):
        self.key = key
        self.text = text
        self.severity = severity

    def to_dict(self):
        return {'key': self.key, 'text': self.text, 'severity': self.severity.value}


class AnalyticsResult:
    __slots__ = ('module', 'metrics', 'distributions', 'trends', 'rankings', 'comparisons', 'alerts', 'insights')

    def __init__(self, module):
        self.module = module
        self.metrics = []
        self.distributions = []
        self.trends = []
        self.rankings = []
        self.comparisons = []
        self.alerts = []
        self.insights = []

    def add_metric(self, key, label, value, unit='count', formula='', source_fields=None, precision=0):
        self.metrics.append(Metric(key, label, value, unit, formula, source_fields or [], precision))
        return self

    def add_distribution(self, key, label, items, total):
        self.distributions.append(Distribution(key, label, items, total))
        return self

    def add_trend(self, key, label, data):
        self.trends.append(Trend(key, label, data))
        return self

    def add_ranking(self, key, label, items):
        self.rankings.append(Ranking(key, label, items))
        return self

    def add_comparison(self, indicator, current, previous):
        self.comparisons.append(compare_periods(indicator, current, previous))
        return self

    def add_alert(self, id, module, severity, title, description, count=0, data=None,
                  rule='', value=None, threshold=None, unit='', affected_count=0, evidence=None):
        self.alerts.append(Alert(id, module, severity, title, description, count, data,
                                 rule, value, threshold, unit, affected_count, evidence))
        return self

    def add_insight(self, key, text, severity=Severity.INFO):
        self.insights.append(Insight(key, text, severity))
        return self

    def to_dict(self):
        return {
            'module': self.module,
            'metrics': [m.to_dict() for m in self.metrics],
            'distributions': [d.to_dict() for d in self.distributions],
            'trends': [t.to_dict() for t in self.trends],
            'rankings': [r.to_dict() for r in self.rankings],
            'comparisons': [c.to_dict() for c in self.comparisons],
            'alerts': [a.to_dict() for a in self.alerts],
            'insights': [i.to_dict() for i in self.insights],
        }


# ============================================================
# AGREGACIONES SEGURAS
# ============================================================

def safe_count(records):
    return len(records) if records else 0


def safe_sum(records, field):
    if not records:
        return 0
    total = 0
    for r in records:
        v = r.get(field)
        if v is not None:
            try:
                total += float(v)
            except (TypeError, ValueError):
                pass
    return total


def safe_average(records, field):
    if not records:
        return 0
    vals = []
    for r in records:
        v = r.get(field)
        if v is not None:
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                pass
    return sum(vals) / len(vals) if vals else 0


def safe_min(records, field):
    if not records:
        return None
    vals = []
    for r in records:
        v = r.get(field)
        if v is not None:
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                pass
    return min(vals) if vals else None


def safe_max(records, field):
    if not records:
        return None
    vals = []
    for r in records:
        v = r.get(field)
        if v is not None:
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                pass
    return max(vals) if vals else None


def safe_percentage(part, total):
    if not total:
        return 0.0
    return (part / total) * 100


def safe_ratio(numerator, denominator):
    if not denominator:
        return 0.0
    return numerator / denominator


def count_by_field(records, field):
    counts = {}
    for r in records:
        val = r.get(field, '—')
        counts[val] = counts.get(val, 0) + 1
    return counts


def sum_by_field(records, group_field, value_field):
    totals = {}
    for r in records:
        key = r.get(group_field, '—')
        v = r.get(value_field)
        if v is not None:
            try:
                totals[key] = totals.get(key, 0) + float(v)
            except (TypeError, ValueError):
                pass
    return totals


def group_by(records, field):
    groups = {}
    for r in records:
        key = r.get(field, '—')
        if key not in groups:
            groups[key] = []
        groups[key].append(r)
    return groups


# ============================================================
# MOTOR DE TENDENCIAS
# ============================================================

def _parse_date(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, _date):
        return datetime(value.year, value.month, value.day)
    if not value:
        return None
    s = str(value).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%Y %H:%M'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _truncate_period(dt, granularity):
    if granularity == 'day':
        return dt.strftime('%Y-%m-%d')
    elif granularity == 'week':
        iso = dt.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    elif granularity == 'month':
        return dt.strftime('%Y-%m')
    return dt.strftime('%Y-%m-%d')


def _next_period(period, granularity):
    if granularity == 'month':
        y, m = int(period[:4]), int(period[5:7])
        m += 1
        if m > 12:
            m = 1
            y += 1
        return f"{y}-{m:02d}"
    elif granularity == 'week':
        parts = period.split('-W')
        y, w = int(parts[0]), int(parts[1])
        d = datetime.strptime(f"{y} {w} 1", "%Y %W %w")
        d += timedelta(weeks=1)
        iso = d.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    elif granularity == 'day':
        parts = period.split('-')
        d = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
        d += timedelta(days=1)
        return d.strftime('%Y-%m-%d')
    return period


def _period_sort_key(period, granularity):
    if granularity == 'month':
        return period
    elif granularity == 'week':
        return period
    elif granularity == 'day':
        return period
    return period


def compute_trend(records, date_field, value_field=None, aggregation='count', granularity='month', label=''):
    if not records:
        return Trend(key=f'trend_{date_field}', label=label or f'Tendencia por {date_field}', data=[])

    buckets = {}
    for r in records:
        dt = _parse_date(r.get(date_field))
        if dt is None:
            continue
        period = _truncate_period(dt, granularity)
        if period not in buckets:
            buckets[period] = []
        if value_field:
            v = r.get(value_field)
            if v is not None:
                try:
                    buckets[period].append(float(v))
                except (TypeError, ValueError):
                    pass
        else:
            buckets[period].append(1)

    sorted_periods = sorted(buckets.keys())

    agg_func = {
        'count': lambda vals: len(vals),
        'sum': lambda vals: sum(vals),
        'avg': lambda vals: sum(vals) / len(vals) if vals else 0,
        'min': lambda vals: min(vals) if vals else 0,
        'max': lambda vals: max(vals) if vals else 0,
    }.get(aggregation, lambda vals: len(vals))

    points = []
    prev_value = None
    for period in sorted_periods:
        value = agg_func(buckets[period])
        abs_change = None
        pct_change = None
        if prev_value is not None:
            abs_change = value - prev_value
            pct_change = safe_percentage(value - prev_value, prev_value) if prev_value != 0 else None
        points.append(TrendPoint(period, value, prev_value, abs_change, pct_change))
        prev_value = value

    key = f'trend_{value_field or "count"}_{date_field}'
    return Trend(key=key, label=label or f'Tendencia de {aggregation} por {date_field}', data=points)


# ============================================================
# MOTOR DE COMPARATIVAS
# ============================================================

def compare_periods(indicator, current, previous):
    if current is None or previous is None:
        return Comparison(indicator, current, previous, None, None, Direction.NOT_COMPARABLE)

    try:
        c = float(current)
        p = float(previous)
    except (TypeError, ValueError):
        return Comparison(indicator, current, previous, None, None, Direction.NOT_COMPARABLE)

    abs_change = c - p
    pct_change = safe_percentage(c - p, p) if p != 0 else None

    if abs_change > 0:
        direction = Direction.UP
    elif abs_change < 0:
        direction = Direction.DOWN
    else:
        direction = Direction.UNCHANGED

    return Comparison(indicator, c, p, abs_change, pct_change, direction)


def compare_dicts(current_kpis, previous_kpis, skip_keys=None):
    skip = set(skip_keys or [])
    results = []
    for key, current_val in current_kpis.items():
        if key in skip:
            continue
        prev_val = previous_kpis.get(key)
        if prev_val is not None:
            results.append(compare_periods(key, current_val, prev_val))
    return results


# ============================================================
# MOTOR DE RANKINGS
# ============================================================

def compute_ranking(records, group_field, value_field=None, aggregation='count', top_n=None, bottom_n=None, order='desc', label=''):
    if not records:
        return Ranking(key=f'ranking_{group_field}', label=label or f'Ranking por {group_field}', items=[])

    groups = group_by(records, group_field)

    agg_func = {
        'count': lambda recs: len(recs),
        'sum': lambda recs: safe_sum(recs, value_field),
        'avg': lambda recs: safe_average(recs, value_field),
        'min': lambda recs: safe_min(recs, value_field) or 0,
        'max': lambda recs: safe_max(recs, value_field) or 0,
    }.get(aggregation, lambda recs: len(recs))

    ranked = []
    for group_val, group_recs in groups.items():
        val = agg_func(group_recs)
        ranked.append((group_val, val))

    reverse = (order == 'desc')
    ranked.sort(key=lambda x: x[1], reverse=reverse)

    if top_n is not None:
        ranked = ranked[:top_n]
    elif bottom_n is not None:
        ranked = ranked[-bottom_n:] if bottom_n <= len(ranked) else ranked

    items = [RankingItem(item=str(item), value=val, position=i + 1) for i, (item, val) in enumerate(ranked)]

    key = f'ranking_{group_field}_{aggregation}'
    return Ranking(key=key, label=label or f'Ranking de {aggregation} por {group_field}', items=items)


# ============================================================
# MOTOR DE DISTRIBUCIONES
# ============================================================

def compute_distribution(records, field, label=''):
    if not records:
        return Distribution(key=f'dist_{field}', label=label or f'Distribución por {field}', items=[], total=0)

    counts = count_by_field(records, field)
    total = sum(counts.values())

    items = []
    for category, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        pct = safe_percentage(count, total)
        items.append(DistributionItem(category=str(category), count=count, percentage=round(pct, 1)))

    return Distribution(key=f'dist_{field}', label=label or f'Distribución por {field}', items=items, total=total)


# ============================================================
# SISTEMA DE UMBRALES
# ============================================================

class Threshold:
    __slots__ = ('id', 'field', 'operator', 'value', 'severity')

    OPERATORS = {
        'gt': lambda a, b: a > b,
        'gte': lambda a, b: a >= b,
        'lt': lambda a, b: a < b,
        'lte': lambda a, b: a <= b,
        'eq': lambda a, b: a == b,
        'neq': lambda a, b: a != b,
    }

    def __init__(self, id, field, operator, value, severity=Severity.WARNING):
        self.id = id
        self.field = field
        self.operator = operator
        self.value = value
        self.severity = severity

    def evaluate(self, record):
        val = record.get(self.field)
        if val is None:
            return False
        try:
            return self.OPERATORS[self.operator](float(val), float(self.value))
        except (TypeError, ValueError, KeyError):
            return False


class ThresholdGroup:
    def __init__(self, thresholds=None):
        self.thresholds = list(thresholds or [])

    def add(self, threshold):
        self.thresholds.append(threshold)
        return self

    def evaluate(self, records):
        alerts = []
        for t in self.thresholds:
            triggered = [r for r in records if t.evaluate(r)]
            if triggered:
                evidence = AlertEvidence(
                    affected_count=len(triggered),
                    sample_records=triggered[:10],
                )
                alerts.append(Alert(
                    id=t.id, module='', severity=t.severity,
                    title=t.id, description=f'{len(triggered)} registros superan umbral',
                    value=len(triggered), threshold=t.value, unit='count',
                    affected_count=len(triggered), evidence=evidence,
                ))
        return alerts


# ============================================================
# UTILIDADES DE FECHA
# ============================================================

def parse_date(value):
    return _parse_date(value)


def truncate_period(dt, granularity):
    return _truncate_period(dt, granularity)


def filter_by_date_range(records, date_field, start_date, end_date):
    start = _parse_date(start_date) if isinstance(start_date, str) else start_date
    end = _parse_date(end_date) if isinstance(end_date, str) else end_date

    if not start or not end:
        return records

    result = []
    for r in records:
        dt = _parse_date(r.get(date_field))
        if dt is None:
            result.append(r)
            continue
        if start <= dt <= end:
            result.append(r)
    return result


def filter_by_date_range_exclusive_end(records, date_field, start_date, end_date):
    start = _parse_date(start_date) if isinstance(start_date, str) else start_date
    end = _parse_date(end_date) if isinstance(end_date, str) else end_date

    if not start or not end:
        return records

    end_exclusive = end + timedelta(days=1)

    result = []
    for r in records:
        dt = _parse_date(r.get(date_field))
        if dt is None:
            result.append(r)
            continue
        if start <= dt < end_exclusive:
            result.append(r)
    return result


def shift_period(start_date, end_date, periods_back=1):
    s = _parse_date(start_date) if isinstance(start_date, str) else start_date
    e = _parse_date(end_date) if isinstance(end_date, str) else end_date

    if not s or not e:
        return None, None

    delta = e - s
    new_start = s - delta
    new_end = s - timedelta(days=1)
    return new_start, new_end


# ============================================================
# MOTOR DE ALERTAS DETERMINÍSTICAS
# ============================================================

class AlertEvidence:
    __slots__ = ('affected_count', 'sample_records', 'aggregate_value', 'aggregate_field')

    def __init__(self, affected_count, sample_records=None, aggregate_value=None, aggregate_field=''):
        self.affected_count = affected_count
        self.sample_records = sample_records or []
        self.aggregate_value = aggregate_value
        self.aggregate_field = aggregate_field

    def to_dict(self):
        d = {'affected_count': self.affected_count, 'sample_records': self.sample_records}
        if self.aggregate_value is not None:
            d['aggregate_value'] = self.aggregate_value
            d['aggregate_field'] = self.aggregate_field
        return d


class AlertRule:
    __slots__ = ('id', 'module', 'title', 'description_template', 'severity', 'evaluator')

    def __init__(self, id, module, title, description_template, severity, evaluator):
        self.id = id
        self.module = module
        self.title = title
        self.description_template = description_template
        self.severity = severity
        self.evaluator = evaluator

    def evaluate(self, records, today=None):
        return self.evaluator(records, today=today)


def _parse_date_safe(value):
    return _parse_date(value)


# --- EVALUADORES GENÉRICOS ---

def eval_field_threshold(field, operator, threshold_value, severity=Severity.WARNING):
    ops = {
        'gt': lambda a, b: a > b,
        'gte': lambda a, b: a >= b,
        'lt': lambda a, b: a < b,
        'lte': lambda a, b: a <= b,
        'eq': lambda a, b: a == b,
        'neq': lambda a, b: a != b,
    }
    op_fn = ops.get(operator)
    if not op_fn:
        return lambda recs, today=None: []

    def evaluator(records, today=None):
        triggered = []
        for r in records:
            val = r.get(field)
            if val is None:
                continue
            try:
                if op_fn(float(val), float(threshold_value)):
                    triggered.append(r)
            except (TypeError, ValueError):
                continue
        if not triggered:
            return []
        evidence = AlertEvidence(
            affected_count=len(triggered),
            sample_records=triggered[:10],
        )
        return [Alert(
            id=f'{field}_{operator}_{threshold_value}',
            module='', severity=severity,
            title=f'{field} {operator} {threshold_value}',
            description=f'{len(triggered)} registros cumplen {field} {operator} {threshold_value}',
            value=len(triggered), threshold=threshold_value, unit='count',
            affected_count=len(triggered), evidence=evidence,
        )]
    return evaluator


def eval_count_above(threshold_value, severity=Severity.WARNING):
    def evaluator(records, today=None):
        count = len(records) if records else 0
        if count > threshold_value:
            evidence = AlertEvidence(affected_count=count, sample_records=records[:10])
            return [Alert(
                id=f'count_gt_{threshold_value}',
                module='', severity=severity,
                title=f'Cantidad superior a {threshold_value}',
                description=f'{count} registros superan umbral de {threshold_value}',
                value=count, threshold=threshold_value, unit='count',
                affected_count=count, evidence=evidence,
            )]
        return []
    return evaluator


def eval_percentage_above(numerator_field, denominator_field, threshold_pct, severity=Severity.WARNING):
    def evaluator(records, today=None):
        num = 0
        den = 0
        for r in records:
            n = r.get(numerator_field)
            d = r.get(denominator_field)
            if n is not None and d is not None:
                try:
                    num += float(n)
                    den += float(d)
                except (TypeError, ValueError):
                    pass
        if den == 0:
            return []
        pct = (num / den) * 100
        if pct > threshold_pct:
            return [Alert(
                id=f'pct_{numerator_field}_{threshold_pct}',
                module='', severity=severity,
                title=f'Porcentaje superior a {threshold_pct}%',
                description=f'{pct:.1f}% supera umbral de {threshold_pct}%',
                value=round(pct, 1), threshold=threshold_pct, unit='percent',
                affected_count=len(records),
                evidence=AlertEvidence(affected_count=len(records), aggregate_value=round(pct, 1), aggregate_field=f'{numerator_field}/{denominator_field}'),
            )]
        return []
    return evaluator


def eval_date_expired(date_field, severity=Severity.CRITICAL):
    def evaluator(records, today=None):
        now = today or datetime.now()
        if isinstance(now, _date) and not isinstance(now, datetime):
            now = datetime(now.year, now.month, now.day)
        expired = []
        for r in records:
            dt = _parse_date_safe(r.get(date_field))
            if dt is None:
                continue
            if dt < now:
                expired.append(r)
        if not expired:
            return []
        evidence = AlertEvidence(affected_count=len(expired), sample_records=expired[:10])
        return [Alert(
            id=f'date_expired_{date_field}',
            module='', severity=severity,
            title=f'Fecha vencida: {date_field}',
            description=f'{len(expired)} registros con {date_field} vencido',
            value=len(expired), threshold=0, unit='count',
            affected_count=len(expired), evidence=evidence,
        )]
    return evaluator


def eval_date_expiring(date_field, days, severity=Severity.WARNING):
    def evaluator(records, today=None):
        now = today or datetime.now()
        if isinstance(now, _date) and not isinstance(now, datetime):
            now = datetime(now.year, now.month, now.day)
        limit = now + timedelta(days=days)
        expiring = []
        for r in records:
            dt = _parse_date_safe(r.get(date_field))
            if dt is None:
                continue
            if now <= dt <= limit:
                expiring.append(r)
        if not expiring:
            return []
        evidence = AlertEvidence(affected_count=len(expiring), sample_records=expiring[:10])
        return [Alert(
            id=f'date_expiring_{date_field}_{days}d',
            module='', severity=severity,
            title=f'Vence en {days} días: {date_field}',
            description=f'{len(expiring)} registros vencen en {days} días o menos',
            value=len(expiring), threshold=days, unit='days',
            affected_count=len(expiring), evidence=evidence,
        )]
    return evaluator


def eval_age_above(date_field, days, severity=Severity.WARNING):
    def evaluator(records, today=None):
        now = today or datetime.now()
        if isinstance(now, _date) and not isinstance(now, datetime):
            now = datetime(now.year, now.month, now.day)
        old = []
        for r in records:
            dt = _parse_date_safe(r.get(date_field))
            if dt is None:
                continue
            age = (now - dt).days
            if age > days:
                r_copy = dict(r)
                r_copy['_age_days'] = age
                old.append(r_copy)
        if not old:
            return []
        evidence = AlertEvidence(affected_count=len(old), sample_records=old[:10])
        return [Alert(
            id=f'age_{date_field}_{days}d',
            module='', severity=severity,
            title=f'Antigüedad superior a {days} días',
            description=f'{len(old)} registros con más de {days} días desde {date_field}',
            value=len(old), threshold=days, unit='days',
            affected_count=len(old), evidence=evidence,
        )]
    return evaluator


def eval_concentration(group_field, value_field, top_n, threshold_pct, severity=Severity.WARNING):
    def evaluator(records, today=None):
        if not records:
            return []
        groups = {}
        for r in records:
            key = r.get(group_field, '—')
            v = r.get(value_field)
            if v is not None:
                try:
                    groups[key] = groups.get(key, 0) + float(v)
                except (TypeError, ValueError):
                    pass
        if not groups:
            return []
        total = sum(groups.values())
        if total == 0:
            return []
        sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
        top = sorted_groups[:top_n]
        top_sum = sum(v for _, v in top)
        pct = (top_sum / total) * 100
        if pct > threshold_pct:
            return [Alert(
                id=f'concentration_{group_field}_{top_n}',
                module='', severity=severity,
                title=f'Concentración en top {top_n} {group_field}',
                description=f'Top {top_n} representan {pct:.1f}% del total',
                value=round(pct, 1), threshold=threshold_pct, unit='percent',
                affected_count=top_n,
                evidence=AlertEvidence(
                    affected_count=top_n,
                    sample_records=[{group_field: k, value_field: v} for k, v in top],
                    aggregate_value=round(pct, 1), aggregate_field=group_field,
                ),
            )]
        return []
    return evaluator


def eval_range_outside(field, min_val=None, max_val=None, severity=Severity.WARNING):
    def evaluator(records, today=None):
        outside = []
        for r in records:
            val = r.get(field)
            if val is None:
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            if min_val is not None and v < min_val:
                outside.append(r)
            elif max_val is not None and v > max_val:
                outside.append(r)
        if not outside:
            return []
        evidence = AlertEvidence(affected_count=len(outside), sample_records=outside[:10])
        return [Alert(
            id=f'range_{field}_{min_val}_{max_val}',
            module='', severity=severity,
            title=f'Valor fuera de rango: {field}',
            description=f'{len(outside)} registros fuera de rango [{min_val}, {max_val}]',
            value=len(outside), threshold=min_val or max_val, unit='count',
            affected_count=len(outside), evidence=evidence,
        )]
    return evaluator


# --- EVALUADORES COMPUESTOS ---

def eval_and(*evaluators):
    def evaluator(records, today=None):
        all_alerts = []
        for ev in evaluators:
            alerts = ev(records, today=today)
            all_alerts.extend(alerts)
        if len(all_alerts) == len(evaluators):
            return all_alerts
        return []
    return evaluator


def eval_or(*evaluators):
    def evaluator(records, today=None):
        all_alerts = []
        for ev in evaluators:
            alerts = ev(records, today=today)
            all_alerts.extend(alerts)
        return all_alerts
    return evaluator


# --- DEDUPLICACIÓN ---

def deduplicate_alerts(alerts):
    seen = {}
    result = []
    for a in alerts:
        key = (a.id, a.module, a.severity.value if hasattr(a.severity, 'value') else a.severity)
        if key not in seen:
            seen[key] = a
            result.append(a)
        else:
            existing = seen[key]
            existing.affected_count = max(existing.affected_count, a.affected_count)
    return result


# --- ALERTA MEJORADA ---

class EnhancedAlert:
    __slots__ = ('id', 'module', 'rule', 'severity', 'title', 'description',
                 'value', 'threshold', 'unit', 'affected_count', 'evidence', 'metadata')

    def __init__(self, id, module, rule, severity, title, description,
                 value=None, threshold=None, unit='', affected_count=0,
                 evidence=None, metadata=None):
        self.id = id
        self.module = module
        self.rule = rule
        self.severity = severity
        self.title = title
        self.description = description
        self.value = value
        self.threshold = threshold
        self.unit = unit
        self.affected_count = affected_count
        self.evidence = evidence
        self.metadata = metadata or {}

    def to_dict(self):
        d = {
            'id': self.id, 'module': self.module, 'rule': self.rule,
            'severity': self.severity.value if hasattr(self.severity, 'value') else self.severity,
            'title': self.title, 'description': self.description,
            'value': self.value, 'threshold': self.threshold, 'unit': self.unit,
            'affected_count': self.affected_count,
        }
        if self.evidence:
            d['evidence'] = self.evidence.to_dict()
        if self.metadata:
            d['metadata'] = self.metadata
        return d


# --- REGISTRO DE REGLAS POR MÓDULO ---

ALERT_RULES_REGISTRY = {}


def register_alert_rules(module, rules):
    ALERT_RULES_REGISTRY[module] = rules


def get_alert_rules(module):
    return ALERT_RULES_REGISTRY.get(module, [])


def evaluate_module_alerts(module, records, today=None):
    rules = get_alert_rules(module)
    all_alerts = []
    for rule in rules:
        alerts = rule.evaluate(records, today=today)
        for a in alerts:
            a.module = module
        all_alerts.extend(alerts)
    return deduplicate_alerts(all_alerts)
