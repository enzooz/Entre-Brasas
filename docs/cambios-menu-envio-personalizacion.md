# Cambios solicitados — 30/09/2026

Proyecto: Entre Brasas. Rama verificada: `beta-nico`.

Solicitud implementada después de confirmar la rama y verificar el remoto. Sin commit; se preservan los cambios existentes del rediseño.

## 1. Reemplazar el catálogo por el menú del local

Fuente: captura del menú proporcionada por el usuario. Todas las hamburguesas incluyen papas.

| Hamburguesa | Precio | Descripción |
| --- | ---: | --- |
| Sagrada | $16.500 | Pan brioche, 3 medallones, cheddar y aderezo de la casa. |
| Full | $15.500 | Pan brioche, 2 medallones, cheddar, panceta, huevo, cebolla caramelizada y aderezo alioli. |
| La Pepi | $14.000 | Pan brioche, 2 medallones, cheddar, cebolla en brunoise, pepinillos y aderezo de la casa. |
| Crispy | $13.500 | Pan brioche, 1 medallón, cheddar, panceta, cebolla crispy y aderezo alioli. |
| Freskita | $11.500 | Pan brioche, 1 medallón, cheddar, lechuga, tomate, cebolla morada y aderezo de la casa. |
| Baconera | $13.500 | Pan brioche, 2 medallones, cheddar, panceta y aderezo de la casa. |
| Tradi | $11.500 | Pan brioche, 1 medallón, queso tybo, jamón, tomate, lechuga y mayonesa. |
| Cheese | $10.500 | Pan brioche, 1 medallón, cheddar y aderezo de la casa. |

Adicionales disponibles para cualquier hamburguesa:

| Adicional | Precio |
| --- | ---: |
| Medallón extra | $2.500 |
| Cheddar extra | $1.000 |
| Panceta | $2.000 |
| Huevo | $1.000 |
| Papas fritas | $2.000 |

Al implementar, conservar el historial de pedidos y sus precios guardados. Evitar borrar productos antiguos si eso elimina registros relacionados; retirarlos del catálogo activo.

## 2. Envío por cada 100 metros

- La configuración debe expresar la tarifa por 100 metros, no por kilómetro entero.
- La distancia se sigue ingresando en kilómetros: `0,1` equivale a 100 metros.
- Los nuevos pedidos y la distancia mínima de configuración aceptan hasta un decimal (pasos de 100 metros). Se rechazan valores como `5,45` sin redondearlos silenciosamente. Las distancias de pedidos históricos se conservan.
- Cobrar la distancia ingresada sin redondearla a kilómetros enteros: `5,4 km` corresponde a 54 tramos de 100 metros.
- Mantener coherentes el cálculo del navegador, el cálculo del servidor y las unidades que muestra la configuración.
- No confundir el redondeo monetario con el redondeo de la distancia.

## 3. Personalizar cada hamburguesa individualmente

- Cada unidad agregada en Nuevo pedido debe generar su propio bloque completo de personalización.
- Agregar dos hamburguesas iguales debe mostrar dos bloques separados, con adicionales y nota para cocina independientes.
- Un adicional elegido en una unidad no debe aplicarse automáticamente a las demás.
- Ejemplo del usuario: dos BBQ, pero solo una con bacon extra. Con el catálogo nuevo, aplicar el mismo comportamiento a cualquiera de las hamburguesas disponibles.
- Verificar también pedidos completados desde mensajes y que el total y la comanda respeten cada unidad.

## Estado

Implementado el 30/09/2026:

- Base local actualizada con las 8 hamburguesas y los 5 adicionales de la captura. Productos anteriores desactivados, no eliminados.
- `seed_data --reemplazar-menu` permite repetir la actualización sin duplicar productos ni borrar pedidos, movimientos, stock o configuración. Las cantidades de recetas ya existentes se conservan; las recetas nuevas usan las estimaciones documentadas en el comando original y deben confirmarse con el local.
- Migración `config.0003_tarifa_por_100_metros`: convierte la tarifa anterior dividiéndola por 10 para mantener el precio equivalente. La base local pasó de $500/km a $50/100 m.
- El navegador y el servidor calculan la distancia decimal exacta. Cuando se alcanza la distancia mínima para cobrar, el envío es **importe base + tarifa por toda la distancia**, no el mayor de ambos. Ejemplo: mínimo $1.000 + 54 × $50 para 5,4 km = $3.700. Se conserva el retiro gratis y la distancia gratis; no se recalculan pedidos históricos.
- Cada toque en el menú y las cantidades importadas desde WhatsApp generan unidades separadas. Los pedidos nuevos se guardan con un item por unidad; notas y adicionales son independientes.
- Los medallones extra indican su cantidad y precio, evitando llamar “simple” a productos que ya traen varios medallones. La comanda explicita los medallones añadidos.
- 23 pruebas automáticas aprobadas, incluyendo conversión de tarifa, historial conservado, extras individuales, descuento de stock y WhatsApp.
- Respaldo previo: `app/copias_de_seguridad/entre_brasas_2026-09-30_15-36.sqlite3`.
- Verificación directa contra el respaldo: todos los registros anteriores de pedidos, items, adicionales de pedidos, historial de estados, movimientos e ingredientes quedaron intactos.

### Ajuste posterior solicitado

- Quitado el botón Agregar otra. Para sumar unidades se vuelve a tocar el producto en el menú.
- Hamburguesas y Adicionales muestran solo activos. Los productos anteriores se conservan en la base exclusivamente para preservar historial y relaciones; no aparecen en estos listados.
- Inventario, sus avisos en Inicio y el selector de Registrar movimiento muestran solo ingredientes activos usados por hamburguesas activas o por adicionales activos disponibles en esas hamburguesas. No se borran existencias ni movimientos anteriores. Ingredientes y Recetas conservan sus herramientas de administración para poder dar de alta nuevos insumos y asociarlos al menú.
- Verificación del ajuste: 34 pruebas aprobadas; navegador confirma 8 hamburguesas activas, 5 adicionales activos y 18 ingredientes del menú activo. Dos toques en Baconera siguen creando dos unidades y no hay botones Agregar otra. Se respetaron los precios actuales editados por el usuario; este ajuste no vuelve a ejecutar la carga de datos iniciales.
