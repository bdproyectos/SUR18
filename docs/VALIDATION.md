# Validación del piloto

El caso **Planta Andina – Cochabamba** usa el archivo `examples/planta_andina_input.json`. Al ejecutar `project.sur18_pv.calculate(...)`, los valores principales deben coincidir con `planta_andina_resultado_esperado.json`:

- 400 módulos de 550 Wp (220 kWp DC).
- 20 strings de 20 módulos.
- 2 inversores de 100 kW AC.
- 351 780 kWh/año estimados, equivalente a 73,29 % del consumo de referencia.

Antes de producción, realice también estas pruebas en el Gateway:

1. Un string con Voc corregido por frío menor que la tensión máxima DC del inversor.
2. Vmp corregido por calor dentro de la ventana MPPT.
3. Superficie, peso y cargas estructurales aprobadas.
4. Dos guardados del mismo proyecto generan revisiones consecutivas.
5. El botón Google Earth abre el punto de coordenadas y el KML se visualiza correctamente.

