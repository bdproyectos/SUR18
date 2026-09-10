# Reporte PDF de proyecto FV

El piloto genera un PDF A4 de cuatro páginas mediante el módulo Reporting de Ignition. El botón de Perspective llama a project.sur18_report.download_pdf(projectId, projectCode, revision). Esto crea el archivo en memoria y lo descarga, sin dejar archivos temporales en el Gateway.

## Parámetro y fuentes de datos

Crear el reporte Informes/Proyecto FV en el proyecto SUR18_Solar_Designer. Definir el parámetro Long project_id. Agregar estas fuentes de datos Query, configuradas contra SUR18_PV:

### Proyecto
~~~sql
SELECT p.project_id, p.code, p.name, p.client_name, p.address, p.latitude, p.longitude,
       p.timezone, p.status, p.created_at, p.updated_at
FROM projects p WHERE p.project_id = :project_id;
~~~

### Último diseño
~~~sql
SELECT d.design_id, d.revision, d.name, d.created_at, d.created_by, d.notes,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.dc_kwp')) AS dc_kwp,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.ac_kw')) AS ac_kw,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.module_count')) AS module_count,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.module_power_w')) AS module_power_w,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.string_count')) AS string_count,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.modules_per_string')) AS modules_per_string,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.inverter_count')) AS inverter_count,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.annual_energy_kwh')) AS annual_energy_kwh,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.actual_coverage_pct')) AS actual_coverage_pct,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.used_module_area_m2')) AS used_module_area_m2,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.estimated_gross_area_m2')) AS estimated_gross_area_m2,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.layout_rows')) AS layout_rows,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.layout_columns')) AS layout_columns,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.voc_string_cold_v')) AS voc_string_cold_v,
  JSON_UNQUOTE(JSON_EXTRACT(d.result_json, '$.vmp_string_hot_v')) AS vmp_string_hot_v,
  d.input_json, d.result_json
FROM designs d WHERE d.project_id = :project_id ORDER BY d.revision DESC LIMIT 1;
~~~

### Historial
~~~sql
SELECT revision, name, created_at, created_by,
  JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.dc_kwp')) AS dc_kwp,
  JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.annual_energy_kwh')) AS annual_energy_kwh
FROM designs WHERE project_id = :project_id ORDER BY revision DESC;
~~~

## Composición obligatoria

Use margen de 15 mm, pie de página SUR18 Solar Designer - Confidencial - Página X de Y, logotipo corporativo y fuente sans-serif. Active ajuste de texto para dirección, notas y advertencias.

| Página | Contenido |
| --- | --- |
| 1. Resumen ejecutivo | Cliente, código, ubicación, coordenadas, estado, potencia DC/AC, energía anual, cobertura y fecha/revisión. |
| 2. Diseño eléctrico | Ficha de módulos, strings, inversores, relación DC/AC, Voc por frío, Vmp por calor y advertencias. |
| 3. Implantación | Área disponible/ocupada, filas, columnas, GCR, pasillos, croquis de matriz y enlace/QR a Google Earth. |
| 4. Supuestos y trazabilidad | Consumo, irradiación, PR, temperaturas, limitaciones, historial de revisiones, notas y descargo técnico. |

Conserve el reporte en cuatro páginas. Si las notas o el historial no caben, permita una quinta página como anexo, nunca reduzca el texto por debajo de 8 pt.

## Botón de descarga

En la vista Perspective, el evento del botón Generar PDF debe ser:

~~~python
project.sur18_report.download_pdf(
    self.view.custom.project_id,
    self.view.custom.project_code,
    self.view.custom.selected_revision
)
~~~

El módulo Reporting debe estar instalado y licenciado. En modo de prueba, Ignition agrega su marca de agua.

