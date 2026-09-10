# Jython 2.7 / Ignition 8.3. Motor de prefactibilidad FV C&I.
# Los resultados no sustituyen el diseño eléctrico, estructural ni normativo.
import math
import json

DB_CONNECTION = 'SUR18_PV'
MODEL_VERSION = '0.2.0-pilot'
MONTHS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
DEFAULT_MONTHLY_FACTORS = [0.079, 0.076, 0.080, 0.081, 0.084, 0.088, 0.091, 0.092, 0.088, 0.084, 0.079, 0.078]

def _number(data, key, minimum=None, maximum=None):
    try:
        value = float(data[key])
    except (KeyError, TypeError, ValueError):
        raise ValueError('El campo %s es obligatorio y numérico.' % key)
    if minimum is not None and value < minimum:
        raise ValueError('%s debe ser mayor o igual a %s.' % (key, minimum))
    if maximum is not None and value > maximum:
        raise ValueError('%s debe ser menor o igual a %s.' % (key, maximum))
    return value

def _optional_number(data, key, default, minimum=None, maximum=None):
    if data.get(key) in (None, ''):
        return float(default)
    return _number(data, key, minimum, maximum)

def _round(value, decimals=2):
    return round(float(value), decimals)

def _monthly_factors(data):
    values = data.get('monthly_generation_factors', DEFAULT_MONTHLY_FACTORS)
    if not isinstance(values, (list, tuple)) or len(values) != 12:
        raise ValueError('monthly_generation_factors debe contener 12 valores.')
    factors = [float(value) for value in values]
    if min(factors) < 0 or sum(factors) <= 0:
        raise ValueError('Los factores mensuales deben ser positivos.')
    total = sum(factors)
    return [value / total for value in factors]

def calculate(data):
    """Dimensionamiento preliminar FV C&I y evaluación económica simple."""
    consumption = _number(data, 'annual_consumption_kwh', 1)
    irradiation = _number(data, 'irradiation_kwh_m2_year', 1)
    pr = _number(data, 'performance_ratio', 0.01, 1)
    coverage_target = _number(data, 'target_coverage_pct', 1, 100) / 100.0
    module_w = _number(data, 'module_power_w', 1)
    voc = _number(data, 'module_voc', 0.1)
    vmp = _number(data, 'module_vmp', 0.1)
    isc = _number(data, 'module_isc', 0.1)
    voc_coeff = _number(data, 'voc_temp_coeff_pct_c', -5, 0) / 100.0
    min_temp = _number(data, 'min_temp_c', -50, 50)
    max_temp = _number(data, 'max_temp_c', -20, 100)
    inv_kw = _number(data, 'inverter_ac_kw', 0.1)
    inv_max_v = _number(data, 'inverter_max_dc_v', 1)
    mppt_min = _number(data, 'inverter_mppt_min_v', 1)
    mppt_max = _number(data, 'inverter_mppt_max_v', mppt_min)
    area = _number(data, 'available_area_m2', 1)
    module_area = _number(data, 'module_area_m2', 0.01)
    gcr = _number(data, 'gcr', 0.05, 1)
    dcac_target = _number(data, 'dc_ac_ratio', 0.5, 2)
    per_row = int(_number(data, 'modules_per_row', 1))
    clearance = _number(data, 'row_clearance_m', 0, 10)
    self_consumption_ratio = _optional_number(data, 'self_consumption_pct', 80, 0, 100) / 100.0
    purchase_price = _optional_number(data, 'energy_price_usd_kwh', 0.25, 0, 100)
    export_credit = _optional_number(data, 'export_credit_usd_kwh', 0, 0, 100)
    installed_cost = _optional_number(data, 'installed_cost_usd_wp', 1.50, 0, 100)
    fixed_cost = _optional_number(data, 'fixed_additional_cost_usd', 0, 0, 100000000)
    om_pct = _optional_number(data, 'om_pct_year', 1, 0, 100) / 100.0
    module_length = _optional_number(data, 'module_length_m', 2.28, 0.1, 10)
    module_width = _optional_number(data, 'module_width_m', 1.13, 0.1, 10)
    tilt = _optional_number(data, 'tilt_deg', 15, 0, 60)
    factors = _monthly_factors(data)

    required_dc_kwp = (consumption * coverage_target) / (irradiation * pr)
    modules_energy = int(math.ceil(required_dc_kwp * 1000.0 / module_w))
    modules_area_limit = int(math.floor(area * gcr / module_area))
    modules_target = min(modules_energy, modules_area_limit)
    if modules_target < 1:
        raise ValueError('La superficie disponible no admite ningún módulo.')

    voc_cold = voc * (1 + voc_coeff * (min_temp - 25))
    vmp_hot = vmp * (1 + voc_coeff * (max_temp - 25))
    max_by_voc = int(math.floor(inv_max_v / voc_cold))
    max_by_mppt = int(math.floor(mppt_max / vmp_hot))
    min_by_mppt = int(math.ceil(mppt_min / vmp_hot))
    modules_per_string = min(max_by_voc, max_by_mppt)
    if modules_per_string < min_by_mppt:
        raise ValueError('No existe longitud de string compatible con la ventana MPPT.')

    strings = int(math.floor(float(modules_target) / modules_per_string))
    if strings < 1:
        raise ValueError('El área no permite completar un string FV compatible.')
    modules = strings * modules_per_string
    dc_kwp = modules * module_w / 1000.0
    inverters = int(math.ceil(dc_kwp / (inv_kw * dcac_target)))
    ac_kw = inverters * inv_kw
    dcac_actual = dc_kwp / ac_kw
    annual_energy = dc_kwp * irradiation * pr

    rows = int(math.ceil(float(modules) / per_row))
    used_module_area = modules * module_area
    projected_length = module_length * math.cos(math.radians(tilt))
    row_pitch = projected_length + clearance
    footprint = rows * row_pitch * per_row * module_width
    area_utilization = footprint / area * 100.0

    self_consumed = annual_energy * self_consumption_ratio
    exports = annual_energy - self_consumed
    grid_import = max(consumption - self_consumed, 0)
    direct_coverage = self_consumed / consumption * 100.0
    generation_ratio = annual_energy / consumption * 100.0

    equipment_cost = modules * module_w * installed_cost
    investment = equipment_cost + fixed_cost
    om_cost = investment * om_pct
    avoided_purchase = self_consumed * purchase_price
    export_revenue = exports * export_credit
    first_year_benefit = avoided_purchase + export_revenue - om_cost
    payback_years = investment / first_year_benefit if first_year_benefit > 0 else None

    monthly_balance = []
    for index in range(12):
        generation = annual_energy * factors[index]
        self_month = generation * self_consumption_ratio
        demand = consumption / 12.0
        monthly_balance.append({'month': MONTHS[index], 'generation_kwh': _round(generation),
            'demand_kwh': _round(demand), 'self_consumption_kwh': _round(self_month),
            'export_kwh': _round(generation - self_month), 'grid_import_kwh': _round(max(demand - self_month, 0))})

    warnings = []
    if modules_energy > modules_area_limit:
        warnings.append('La superficie limita la potencia objetivo; se dimensionó la alternativa físicamente admisible.')
    if dcac_actual > 1.35:
        warnings.append('La relación DC/AC supera 1,35. Evalúe clipping y límites del inversor con datos horarios.')
    if footprint > area:
        warnings.append('La huella de filas supera la cubierta disponible. Ajuste GCR, separación, inclinación o módulos por fila.')
    if self_consumption_ratio < 0.7:
        warnings.append('El autoconsumo supuesto es bajo; use datos horarios de carga antes de aprobar la economía.')
    if payback_years is None:
        warnings.append('El beneficio neto anual no es positivo con los supuestos económicos actuales.')

    return {'model_version': MODEL_VERSION, 'dc_kwp': _round(dc_kwp), 'ac_kw': _round(ac_kw),
        'dc_ac_ratio_actual': _round(dcac_actual), 'module_count': modules, 'module_power_w': module_w,
        'string_count': strings, 'modules_per_string': modules_per_string, 'inverter_count': inverters,
        'annual_energy_kwh': _round(annual_energy), 'generation_to_demand_pct': _round(generation_ratio),
        'direct_demand_coverage_pct': _round(direct_coverage), 'self_consumption_kwh': _round(self_consumed),
        'export_kwh': _round(exports), 'grid_import_kwh': _round(grid_import),
        'used_module_area_m2': _round(used_module_area), 'layout_footprint_m2': _round(footprint),
        'area_utilization_pct': _round(area_utilization), 'layout_rows': rows, 'layout_columns': per_row,
        'row_pitch_m': _round(row_pitch), 'voc_string_cold_v': _round(modules_per_string * voc_cold),
        'vmp_string_hot_v': _round(modules_per_string * vmp_hot), 'string_isc_a': _round(isc),
        'investment_usd': _round(investment), 'equipment_cost_usd': _round(equipment_cost),
        'om_cost_year_usd': _round(om_cost), 'avoided_purchase_usd_year': _round(avoided_purchase),
        'export_revenue_usd_year': _round(export_revenue), 'first_year_benefit_usd': _round(first_year_benefit),
        'simple_payback_years': _round(payback_years) if payback_years is not None else None,
        'monthly_balance': monthly_balance, 'warnings': warnings}

def save_design(project_id, name, input_data, result_data, notes, user):
    """Guarda una revisión inmutable y devuelve el número de revisión."""
    revision = system.db.runNamedQuery('Designs/NextRevision', {'project_id': project_id})[0]['revision']
    args = {'project_id': project_id, 'revision': revision, 'name': name,
            'input_json': json.dumps(input_data), 'result_json': json.dumps(result_data),
            'notes': notes or '', 'user': user or 'system'}
    system.db.runNamedQuery('Designs/Save', args)
    return {'project_id': project_id, 'revision': revision, 'model_version': MODEL_VERSION}
