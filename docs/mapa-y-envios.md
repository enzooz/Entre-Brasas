# Mapa y envíos

## Configuración

En **Configuración → Envío** se puede modificar el precio por cada 100 metros,
la distancia incluida (km, hasta un decimal) y el envío mínimo. No hay un
precio fijo en el mapa. Cambiar la tarifa conserva la clave y no recalcula
pedidos históricos. Al volver a Nuevo pedido se usan los valores actualizados.

Fórmula: mínimo + máximo(0, km − km incluidos) × 10 × tarifa por 100 metros.
Ejemplo: mínimo $1.000 hasta 1 km y $100 por 100 metros excedentes:
0,1–1 km = $1.000; 1,1 km = $1.100; 1,3 km = $1.300.
Con tarifa de $200, 1,3 km cuesta $1.600. Retiro en el local cuesta $0.

En **Mapa y direcciones**, cargar una API key de un proyecto Geoapify propio.
El campo se muestra vacío al volver; dejarlo vacío conserva la clave. Para
quitarla, marcar Eliminar la clave guardada y guardar configuración.
La clave queda en la base SQLite y sus respaldos, no cifrada: proteger esos
archivos y no compartirlos. No está en el repositorio, HTML ni borrador.

Comprobar las coordenadas de salida del local. El punto inicial sugerido es
Jujuy 87, Resistencia; una dirección interpolada no garantiza precisión GPS.
Latitud y longitud son coordenadas, NO kilómetros ni metros.

## Cargar un envío

1. En el paso Ubicación elegir Envío a domicilio.
2. Escribir calle y altura o un lugar de Resistencia y tocar Buscar dirección.
3. Elegir el resultado, comprobar el destino y su recorrido en el mapa.
4. Corregir un punto aproximado tocando el mapa o arrastrando el destino.
5. Revisar kilómetros y total antes de crear el pedido.

Geoapify devuelve **metros**: 1.340 metros se truncan a **1,3 km** (no 1,4).
1.494 metros → 1,4 km. 5,4 km significa 5 km y 400 metros. Nunca millas ni
redondeo a kilómetros enteros. El recorrido es por calles en modo auto, sin
tráfico en tiempo real; no representa necesariamente el trayecto de una moto.
Buscar resultados/puntos aproximados requiere comprobar calle y altura.

Se puede ingresar distancia por teclado. Editar dirección invalida una
distancia calculada anterior. Editar kilómetros cancela una ruta pendiente;
una respuesta tardía no sobrescribe ese valor. Cambiar origen del local
invalida las rutas recuperadas. El borrador por pestaña conserva destino y
recorrido sin volver a consultarlos automáticamente.

## Conexión, créditos y privacidad

- Escribir no consulta Geoapify. Un clic Buscar realiza una búsqueda; elegir
  destino o ajustar el punto realiza un recorrido. Consultas idénticas se
  reutilizan por 24 horas. No es autocompletado por cada tecla.
- Límite preventivo: 2.000 créditos/día UTC por instalación; no equivale al
  saldo de la cuenta ni suma otras computadoras que usen la misma clave.
  Revisar el consumo real en el panel de Geoapify. Ante HTTP 429 se evita
  reconsultar por cinco minutos y se ofrece la distancia manual.
- Leaflet está incluido localmente. Los mosaicos son datos OpenStreetMap
  servidos por Geoapify desde el backend: cada mosaico nuevo consume 0,25
  créditos, una búsqueda 1 y un recorrido local básico 1. Sólo se descargan
  para el mapa visible, cacheados 24 horas y con atribución. No hay precarga
  ni garantía de disponibilidad. Fuente: https://www.geoapify.com/pricing-details/
- Buscar envía el texto de dirección a Geoapify; calcular envía coordenadas
  del local y destino. Mostrar/mover el mapa solicita mosaicos a Geoapify.
- Sin clave, cuota o conexión, ingresar kilómetros manualmente. No inventar
  una distancia ni un costo cero ante un fallo. Los cálculos locales, stock y
  pedidos no dependen del servicio externo.

## Desarrollo

La migración `config.0004_mapas_geoapify` agrega campos sin cambiar tarifas,
stock ni pedidos. Usar `python manage.py respaldar` antes de migrar.
Los archivos de `cache_mapas/` están ignorados por Git. Los tests del proveedor
usan claves ficticias y respuestas simuladas, nunca la clave real.

Pruebas: `python manage.py test` y `node --test pedidos/tests_mapas.cjs` desde
`app/`, junto con los tests existentes. Django 4.2 se verifica con Python
3.12. Servidor local Waitress requiere reinicio después de editar backend
o templates cacheados. URLs de mosaicos/atribución pueden cambiarse con
`ENTRE_BRASAS_MAPAS_TILE_URL` y `ENTRE_BRASAS_MAPAS_TILE_ATTRIBUTION`.
