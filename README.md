# SUR18 Solar Designer — piloto para Ignition 8.3

Aplicación base para prefactibilidad, dimensionamiento y diseño preliminar de sistemas fotovoltaicos C&I. Está pensada para ejecutarse en **Ignition 8.3 + Perspective** y MySQL 8.

## Alcance del piloto

- Calcula potencia DC/AC, número de módulos, strings, inversores, área, energía anual y cobertura de demanda.
- Valida límites eléctricos de string con coeficiente de temperatura.
- Propone filas, columnas y área de cubierta, incluyendo pasillos y separaciones.
- Guarda el historial completo de proyectos y sus alternativas de diseño.
- Guarda latitud/longitud y produce un archivo KML o enlace para abrir el emplazamiento en Google Earth.
- Genera un reporte técnico PDF A4 de cuatro páginas por proyecto desde Perspective.
- Incluye el proyecto ejemplo **Planta Andina – Cochabamba**.

> Es una herramienta de ingeniería preliminar. El diseño definitivo debe comprobar sombras, estructura, protecciones, normativa local, capacidad de cortocircuito y estudio eléctrico firmado.

## Instalación

1. En MySQL 8, cree una base de datos y ejecute [`database/001_schema.sql`](database/001_schema.sql), seguido de [`database/002_demo_data.sql`](database/002_demo_data.sql).
2. En el Gateway cree una conexión JDBC llamada `SUR18_PV` y una carpeta de proyecto llamada `SUR18_Solar_Designer`.
3. Copie `ignition_project/SUR18_Solar_Designer` dentro de `data/projects` del Gateway (en Windows normalmente `C:\\Program Files\\Inductive Automation\\Ignition\\data\\projects`) y reinicie el Gateway o espere a que detecte los recursos.
4. Abra Designer, cree una página de Perspective y siga el mapeo de [`docs/PERSPECTIVE_BUILD.md`](docs/PERSPECTIVE_BUILD.md). El código está en los módulos `project.sur18_pv` y `project.sur18_kml`.
5. Cree las Named Queries especificadas en [`docs/NAMED_QUERIES.md`](docs/NAMED_QUERIES.md), usando la conexión `SUR18_PV`.
6. Instale el módulo Reporting y configure el reporte con [`docs/REPORT_PDF.md`](docs/REPORT_PDF.md).

Los archivos de script se guardan como recursos de proyecto para que se puedan versionar con Git. La primera carga desde filesystem debe hacerse en un Gateway de desarrollo; el Designer conserva y completa los metadatos de cada recurso al guardarlo.

## Flujo de uso

1. Registrar cliente y ubicación.
2. Definir consumo anual, irradiación, superficie, módulo e inversor.
3. Ejecutar `sur18_pv.calculate(input)` desde el botón **Calcular**.
4. Mostrar el resultado y persistirlo mediante `sur18_pv.save_design(...)`.
5. Abrir `sur18_kml.earth_url(lat, lon)` o descargar el KML de `sur18_kml.project_kml(...)`.

## Seguridad y despliegue

- Use roles `pv_admin`, `pv_engineer` y `pv_viewer`; no dé acceso de escritura a visitantes.
- El usuario de MySQL debe tener únicamente permisos sobre la base `sur18_pv`.
- No introduzca claves de Google en scripts ni propiedades de Perspective. Google Earth se abre con coordenadas/KML.
- Configure backups de MySQL y de `data/projects`, y revise los cálculos contra fichas técnicas reales.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `ignition_project/` | Proyecto y módulos Python/Jython para Ignition |
| `database/` | Esquema, consultas y proyecto de muestra |
| `docs/` | Guía de montaje de la interfaz Perspective |
| `examples/` | Entrada y resultado del caso de demostración |
