# PLAN DE MEJORAS PENDIENTES — ENTRE BRASAS

**Última actualización:** 25/09/2026
**Origen:** revisión de UX de las pestañas Nuevo Pedido, Cola, Historial, Inventario y
Recetas (lista "PESTAÑA NUEVO PEDIDO"), cruzada contra el código actual.

> La lista original se escribió sobre la versión anterior al refactor `0078897`
> (unificar v1 y v2). Varias cosas ya quedaron resueltas con ese refactor; este
> documento refleja el estado real del código.

---

## ESTADO GENERAL

| Pestaña | Pedido | Estado |
|---|---|---|
| Nuevo pedido | Agregar más de un producto | ✅ Hecho |
| Nuevo pedido | Adicionales por cada producto | ✅ Hecho (ver bug B-1) |
| Nuevo pedido | Ocultar "Distancia" si retira en el local | ✅ Hecho |
| Nuevo pedido | Mostrar el total antes de confirmar | ✅ Hecho |
| Nuevo pedido | Guardar lo escrito con localStorage | ⏳ Pendiente — Tanda 1 |
| Nuevo pedido | Clientes guardados en la base | ⏳ Pendiente — Tanda 3 |
| Cola | Un color por estado (etiqueta, tarjeta y botón) | ✅ Hecho |
| Cola | "Ver detalle" del mismo tamaño que el botón de estado | ✅ Hecho |
| Cola | Barra de búsqueda a ancho completo | ✅ Hecho |
| Cola | Seguir aunque falte stock | ⏳ Pendiente — Tanda 2, falta decisión #2 |
| Historial | Barra de búsqueda a ancho completo | ✅ Hecho |
| Historial | Cambios de estado con fecha y hora | ✅ Hecho |
| Historial | Botón "Eliminar pedido" | ❓ A decidir (#3) |
| Inventario | Unidad de medida al registrar movimiento | ✅ Hecho |
| Inventario | Regla para desactivar ingredientes | ❓ A decidir (#1) |
| Recetas | Quitar la opción "Adicional" | ❓ A decidir (#4) — no se recomienda |

---

## DECISIONES PENDIENTES

### 1. Regla para desactivar ingredientes

**Hoy:** no se puede desactivar un ingrediente que tenga *cualquier* movimiento
registrado (compra, consumo de un pedido o ajuste). Ver
`app/inventario/views.py` → `activar_ingrediente()`.

Por eso el Jamón se pudo desactivar y otros no: el Jamón nunca tuvo movimientos.
Los que sí tienen son Carne molida, Cebolla, Lechuga, Pan y Tomate.

**Problema:** la regla está al revés. Desactivar sirve justamente para "ya no lo
uso, pero quiero conservar el historial".

**Propuesta:** no dejar desactivar un ingrediente que esté en la receta de una
hamburguesa o adicional activos. Ese caso sí rompe el descuento de stock.

**Decisión:** _pendiente_

### 2. Qué pasa con el stock al seguir sin stock suficiente

- **Opción A — stock negativo:** refleja la realidad y el inventario avisa que hay que corregirlo.
- **Opción B — dejarlo en 0:** más prolijo, pero se pierde la señal.

**Recomendación:** A.
**Decisión:** _pendiente_

### 3. Eliminar pedido

El README dice "Nada se borra, se desactiva", y ya existe **Cancelar pedido**, que
pregunta si se devuelve el stock o se registra como pérdida. Borrar un pedido
desarma los reportes de ventas.

**Recomendación:** no agregar "Eliminar". Si molesta ver los cancelados en el
historial, ya existe el filtro "Solo entregados".

**Decisión:** _pendiente_

### 4. Quitar "Adicional" de la pestaña Recetas

Se pidió porque en la versión anterior las recetas de adicionales no descontaban
stock. **Ahora sí lo hacen** (`app/pedidos/calculos.py` → `buscar_recetas_del_item()`).
Si se quita, un adicional como el bacon nunca descuenta bacon.

Hoy hay 0 recetas de adicionales cargadas, por eso parece que no sirve.

**Recomendación:** mantenerla y cargar las recetas de los adicionales.

**Decisión:** _pendiente_

---

## BUGS CONOCIDOS

### B-1 — Dos filas con la misma hamburguesa mezclan los adicionales

**Archivos:** `app/templates/pedidos/crear_pedido.html` y
`app/pedidos/views.py` → `crear_items_del_pedido()`

El campo de adicionales se nombra con el id de la hamburguesa
(`adicionales_3[]`), no con la fila. Si se cargan dos filas de la misma
hamburguesa (por ejemplo, 1 con bacon y 2 sin), la vista le da a las dos filas
los adicionales de ambas.

Es justo el caso de "adicionales según la cantidad de cada producto", así que
hay que arreglarlo antes de dar ese pedido por cerrado.

**Fix:** nombrar el campo con el número de fila (`adicionales_fila_0[]`) y
leerlo por posición en la vista.

---

## TANDA 1 — Cambios chicos

1. **Bug B-1** (ver arriba).
2. **localStorage en Nuevo pedido:** guardar lo escrito para que no se pierda al
   recargar, y limpiarlo cuando el pedido se crea bien.
3. **Regla de ingredientes:** aplicar la decisión #1.

## TANDA 2 — Seguir aunque falte stock

**Archivo:** `app/pedidos/calculos.py` → `descontar_stock()`

La función hace dos pasadas: primero revisa todo el pedido y después descuenta.
Agregar un parámetro `forzar=False` que saltee la revisión. En la cola, cuando
aparece el mensaje de stock insuficiente, ofrecer "Continuar de todos modos".

Depende de la decisión #2.

## TANDA 3 — Clientes

Hoy `Pedido` guarda los datos del cliente como texto suelto (`cliente_nombre`,
`cliente_telefono`, `cliente_direccion`). No existe un modelo `Cliente`.

1. Crear el modelo `Cliente` (nombre, teléfono, dirección, fecha de alta).
2. Agregar un `cliente` opcional en `Pedido`, sin sacar los campos de texto para
   no romper los pedidos viejos.
3. Crear los clientes a partir de los pedidos existentes, agrupando por teléfono.
4. En Nuevo pedido: buscador por teléfono o nombre que complete los datos, más
   la opción "cliente nuevo".

---

## HECHO EN ESTA RONDA (25/09/2026)

- **Colores por estado:** el CSS definía `badge-preparacion` y `badge-camino`,
  pero los templates generan `badge-en_preparacion` y `badge-en_camino`, así que
  esos dos estados no tenían color. Ahora cada estado tiene una variable
  (`--estado-*`) que usan la etiqueta, el borde de la tarjeta y el botón.
- **Botón de avanzar:** dice a qué estado pasa ("Pasar a En camino") y toma el
  color de ese estado. El recorrido de los estados se movió al modelo
  (`Pedido.SIGUIENTE_ESTADO`).
- **Botones de la cola:** "Ver detalle" y el de avanzar ocupan lo mismo. Antes el
  de avanzar quedaba metido en una caja porque heredaba el estilo de los `form`.
- **Filtros:** la cola y el historial usan todo el ancho en una sola fila.
- **Historial del pedido:** muestra los estados con su nombre y color, más el
  renglón de cuando se cargó el pedido. Requirió la migración
  `pedidos/0002_historial_estado_choices` (no cambia la base, solo agrega los
  `choices`).
- **Registrar movimiento:** al elegir el ingrediente, "Cantidad" y "Precio
  unitario" muestran la unidad (kg, L, unidades).
- **Botones rojos que salían azules:** "Cancelar pedido" y "Quitar" (recetas)
  tenían `btn-danger` pero la regla de `button[type="submit"]` les ganaba.

---

## FUERA DE ESTE PLAN

- Módulo "Cerrar el Día" — ver [ideas/cierre-del-dia.md](ideas/cierre-del-dia.md).
