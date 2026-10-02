# Ubicación del pedido

Extensión Operate del cuarto paso existente. El usuario aprobó Geoapify, búsqueda explícita y recorrido integrado; ya proporcionó una clave, guardada únicamente en la base local. Mantener pedido, stock, tarifas y borrador; sin commit.

## Direction contract

THESIS: elegir una dirección y verificar su recorrido sin abandonar el pedido; siempre disponible la distancia manual.

OWN-WORLD: heredar Manrope, azul operativo, superficies blancas y controles de 44px del sistema existente.

STORY: escribir dirección, Buscar, elegir resultado, comprobar destino y distancia, crear pedido. Explicar falta de clave, espera, error y resultados aproximados.

FIRST VIEWPORT: dirección y botón Buscar arriba; resultados debajo; distancia y equivalencias junto al mapa desplegable. Resumen y navegación conservan su posición. En móvil, una columna con mapa opcional compacto.

FORM: extensión local prescrita; sin sorteo ni nuevo mundo visual. Interacción distintiva: seleccionar destino dibuja el recorrido y recalcula el envío; editar dirección invalida la distancia calculada.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

Metros del proveedor convertidos por truncamiento a décimas de km: 1340 m → 1,3 km, nunca millas. Geoapify solo por servidor; Leaflet local y mosaicos OSM servidos por Geoapify, con atribución visible y sin precarga. Cada mosaico nuevo consume 0,25 créditos; caché local 24 horas. Se cambió desde mosaicos públicos OSM porque devolvían imágenes de bloqueo 403 en este entorno. La ubicación inicial del local es sugerida y debe comprobarse.
