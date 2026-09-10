# Jython 2.7 / Ignition 8.3. No depende de librerias externas.
import math
import json

DB_CONNECTION = 'SUR18_PV'

def _number(data, key, minimum=None, maximum=None):
    try:
        value = float(data[key])
    except (KeyError, TypeError, ValueError):
        raise ValueError('El campo %s es obligatorio y numerico.' % key)
    if minimum is not None and value < minimum:
        raise ValueError('%s debe ser mayor o igual a %s.' % (key, minimum))
    if maximum is not None and value > maximum:
        raise ValueError('%s debe ser menor o igual a %s.' % (key, maximum))
    return value

def _round(value, decimals=2):
    return round(value, decimals)

def calculate(data):
    """Devuelve dict serializable con dimensionamiento preliminar FV C&I."""
    consumption = _number(data, 'annual_consumption_kwh', 1)
    irradiation = _number(data, 'irradiation_kwh_m2_year', 1)
    pr = _number(data, 'performance_ratio', 0.01, 1)
    coverage = _number(data, 'target_coverage_pct', 1, 100) / 100.0
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
    dcac = _number(data, 'dc_ac_ratio', 0.5, 2)
    per_row = int(_number(data, 'modules_per_row', 1))
    clearance = _number(data, 'row_clearance_m', 0, 10)

    required_dc_kwp = (consumption * coverage) / (irradiation * pr)
    modules_energy = int(math.ceil(required_dc_kwp * 1000.0 / module_w))
    modules_area_limit = int(math.floor(area * gcr / module_area))
    modules = min(modules_energy, modules_area_limit)
    if modules < 1:
        raise ValueError('La superficie disponible no admite ningún módulo.')

    voc_cold = voc * (1 + voc_coeff * (min_temp - 25))
    vmp_hot = vmp * (1 + voc_coeff * (max_temp - 25))
    max_by_voc = int(math.floor(inv_max_v / voc_cold))
    max_by_mppt = int(math.floor(mppt_max / vmp_hot))
    min_by_mppt = int(math.ceil(mppt_min / vmp_hot))
    modules_per_string = min(max_by_voc, max_by_mppt)
    if modules_per_string < min_by_mppt:
        raise ValueError('No existe longitud de string compatible con la ventana MPPT.')

    strings = int(math.ceil(float(modules) / modules_per_string))
    modules = strings * modules_per_string
    dc_kwp = modules * module_w / 1000.0
    inverters = int(math.ceil(dc_kwp / (inv_kw * dcac)))
    ac_kw = inverters * inv_kw
    annual_energy = dc_kwp * irradiation * pr
    rows = int(math.ceil(float(modules) / per_row))
    used_module_area = modules * module_area
    gross_area = used_module_area / gcr + rows * clearance * math.sqrt(module_area * per_row)
    warnings = []
    if modules_energy > modules_area_limit:
        warnings.append('La superficie limita el objetivo de cobertura; se dimensionó al máximo admisible.')
    if dc_kwp / ac_kw > 1.35:
        warnings.append('La relación DC/AC resultante supera 1.35; confirme clipping y garantía del inversor.')
    if gross_area > area:
        warnings.append('La disposición estimada excede la cubierta; reduzca módulos por fila o aumente GCR/área.')

    return {
        'dc_kwp': _round(dc_kwp), 'ac_kw': _round(ac_kw), 'module_count': modules,
        'module_power_w': module_w, 'string_count': strings,
        'modules_per_string': modules_per_string, 'inverter_count': inverters,
        'annual_energy_kwh': _round(annual_energy),
        'actual_coverage_pct': _round(annual_energy / consumption * 100),
        'used_module_area_m2': _round(used_module_area), 'estimated_gross_area_m2': _round(gross_area),
        'layout_rows': rows, 'layout_columns': per_row,
        'voc_string_cold_v': _round(modules_per_string * voc_cold),
        'vmp_string_hot_v': _round(modules_per_string * vmp_hot),
        'string_isc_a': _round(isc), 'warnings': warnings
    }

def save_design(project_id, name, input_data, result_data, notes, user):
    """Guarda una revisión inmutable y devuelve su design_id."""
    revision = system.db.runNamedQuery('Designs/NextRevision', {'project_id': project_id})[0]['revision']
    args = {'project_id': project_id, 'revision': revision, 'name': name,
            'input_json': json.dumps(input_data), 'result_json': json.dumps(result_data),
            'notes': notes or '', 'user': user or 'system'}
    result = system.db.runNamedQuery('Designs/Save', args)
    return result[0]['design_id']
