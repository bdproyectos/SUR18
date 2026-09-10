# Montaje de la interfaz Perspective

Construya una página principal con navegación a `Inicio`, `Proyectos` y `Diseño`. En el piloto basta una vista de coordenadas con estos controles enlazados a propiedades custom:

| Campo | Propiedad custom | Unidad |
| --- | --- | --- |
| Consumo anual | `custom.design.annual_consumption_kwh` | kWh/año |
| Irradiación en plano | `custom.design.irradiation_kwh_m2_year` | kWh/m²·año |
| Potencia del módulo | `custom.design.module_power_w` | Wp |
| Voc / Vmp / Isc | `custom.design.module_voc`, `module_vmp`, `module_isc` | V / V / A |
| Coeficiente Voc | `custom.design.voc_temp_coeff_pct_c` | %/°C |
| Inversor | `custom.design.inverter_ac_kw`, `inverter_max_dc_v`, `inverter_mppt_min_v`, `inverter_mppt_max_v` | kW / V |
| Temperaturas | `custom.design.min_temp_c`, `max_temp_c` | °C |
| Área / GCR | `custom.design.available_area_m2`, `gcr` | m² / 0–1 |

En el evento `onActionPerformed` del botón **Calcular**:
\`\`\`python
self.view.custom.result = project.sur18_pv.calculate(self.view.custom.design)
\`\`\`

En **Guardar diseño**, después de guardar el proyecto por Named Query:
\`\`\`python
project.sur18_pv.save_design(self.view.custom.project_id, self.view.custom.design_name,
    self.view.custom.design, self.view.custom.result, self.view.custom.notes,
    self.session.props.auth.user.userName)
\`\`\`

Para historial use una Table enlazada a `system.db.runNamedQuery('Designs/ListByProject', {'project_id': projectId})`. Para localizar, añada un botón que ejecute `system.net.openURL(project.sur18_kml.earth_url(lat, lon))`; para descargar KML, use un endpoint Web Dev que retorne `project.sur18_kml.project_kml(...)` con MIME `application/vnd.google-earth.kml+xml`.

