# PLAN DE MEJORAS PENDIENTES — ENTRE BRASAS

**Fecha:** 10/09/2026
**Base:** commit `0dc117b` (05/08/2026)
**Origen:** revisión de UX de las pestañas Nuevo Pedido, Cola, Historial, Inventario y Recetas,
cruzada contra el código actual.

---

## DECISIONES PENDIENTES

Hay tres cosas que hay que definir antes de tocar el código. Cada una cambia la
implementación, no es solo una preferencia estética.

### 1. Regla para desactivar ingredientes

**Hoy:** no se puede desactivar un ingrediente que tenga cualquier movimiento de
inventario registrado.

**Problema:** la regla está invertida. Desactivar sirve justamente para "este
ingrediente ya no lo uso más, pero no quiero borrar el historial". Además el
control también bloquea *reactivar*, así que un ingrediente desactivado que
después recibe un movimiento queda trabado para siempre.

**Propuesta:** reemplazar la regla por "no se puede desactivar un ingrediente que
esté usado en alguna receta activa" — ese sí rompe el descuento de stock.

**Decisión:** _pendiente_

### 2. Qué pasa con el stock al forzar un avance de estado

Cuando se fuerza el paso a "En preparación" sin stock suficiente:

- **Opción A — stock negativo:** refleja la deuda real y el inventario avisa.
- **Opción B — clampear a 0:** más prolijo visualmente, pero se pierde la señal.

**Decisión:** _pendiente_

### 3. Cómo se elimina un pedido

- **Opción A — borrado real:** se borra la fila de la base.
- **Opción B — flag `eliminado`:** sale de las vistas pero queda el registro.

Para un negocio con dinero de por medio conviene la opción B.

**Decisión:** _pendiente_

---

## BUGS ENCONTRADOS

Tres defectos reales detectados al revisar el código. No estaban en la lista
original de mejoras, pero dos de ellos afectan directamente a lo que se pidió.

### BUG-1 — El historial de estados se muestra vacío

**Archivo:** `templates/orders/order_detail.html`, línea 111

El template llama a `h.get_estado_anterior_display` y `h.get_estado_nuevo_display`,
pero los campos `estado_anterior` y `estado_nuevo` de `OrderStatusHistory` son
`CharField` **sin `choices`**. Django solo genera el método `get_FOO_display()`
cuando el campo define choices, así que el template renderiza cadena vacía sin
avisar.

**Resultado actual:** `10/09/2026 14:30 -  →` (los estados no aparecen).

**Fix:** agregar `choices=Order.ESTADOS` a ambos campos del modelo (requiere
migración), o resolver la etiqueta en la vista.

**Relacionado con:** pedido de "mostrar las modificaciones con horario y fecha".

### BUG-2 — La observación al avanzar de estado se descarta

**Archivos:** `templates/orders/order_detail.html` (form de avanzar) y
`apps/orders/views.py` → `advance_order()`

El formulario envía `name="observacion"`, pero la vista nunca lee ese campo:
crea el `OrderStatusHistory` sin observación. Lo que se escribe se pierde.

**Fix:** leer `request.POST.get('observacion', '')` y pasarlo al `create()`.

### BUG-3 — Las recetas de adicionales nunca descontaron stock

**Archivo:** `apps/orders/services.py` → `descontar_stock()`

La función filtra únicamente por `producto_tipo='hamburger'`. Cualquier receta
cargada con `producto_tipo='addon'` es código muerto: nunca se aplica.

El `seed_data.py` tampoco crea recetas de adicionales, así que solo existirían
las cargadas a mano desde la interfaz.

**Nota:** esto respalda la decisión de quitar la opción "Adicional" de la pestaña
Recetas. Ver TANDA 3.

---

## TANDA 1 — Bugs y mejoras de interfaz

Es la mayor parte de la lista original y casi no toca la base de datos.
Se puede hacer de corrido.

### 1.1 Corregir el historial de estados (BUG-1)

Agregar `choices=Order.ESTADOS` a `estado_anterior` y `estado_nuevo` en
`OrderStatusHistory`. Generar migración. Verificar que el detalle del pedido
muestre `fecha - Estado anterior → Estado nuevo` completo.

### 1.2 Guardar la observación del cambio de estado (BUG-2)

Leer el campo en `advance_order()` y guardarlo en el historial.

### 1.3 Arreglar la regla de activar/desactivar ingredientes

**Archivo:** `apps/inventory/views.py` → `toggle_ingredient()`

Aplicar la decisión #1. Como mínimo, mover el control para que solo aplique
al *desactivar*, nunca al reactivar.

### 1.4 Botón "agregar producto" en Nuevo Pedido

**Archivo:** `templates/orders/create_order.html`

El backend ya lo soporta: `crear_items_pedido()` itera sobre `hamburger_ids[]` y
`quantities[]`, y `OrderItem` es una relación uno-a-muchos. El template manda un
solo `<select>`.

Trabajo: clonar el bloque "Producto" con JavaScript, con botón de agregar y
quitar. No requiere cambios en el modelo ni en la vista.

### 1.5 Adicionales por bloque de producto

Hoy el contenedor de adicionales es único (`#addons-container`) y se rearma
cuando cambia el select. Con múltiples productos, cada bloque necesita su propia
lista de adicionales, filtrada por la hamburguesa de *ese* bloque.

El nombre del campo ya está preparado para esto:
`addon_ids_hamburger_<id>[]`.

### 1.6 Ocultar "Distancia (km)" con retiro en local

**Archivo:** `templates/orders/create_order.html`

El `<div id="envio-fields">` ya envuelve el input — quedó preparado y sin
conectar. Agregar el listener al checkbox `#id_retiro_local`. Unas cinco líneas.

### 1.7 Mostrar subtotal antes de confirmar el pedido

Los precios ya viajan al template: `data-precio` en cada option y el objeto
`addonsData` con el precio de cada adicional. Cálculo en el navegador:
productos + adicionales + envío estimado.

### 1.8 Persistir el formulario con localStorage

Guardar lo escrito en Nuevo Pedido para que no se pierda al recargar, **sin**
crear el pedido. Limpiar el almacenamiento al enviar el formulario con éxito.

### 1.9 Unidad de medida al registrar movimiento

**Archivo:** `templates/inventory/form_movement.html`

`Ingredient.unidad` ya existe con sus choices. Pasar las unidades al template
(atributo `data-unidad` en cada option) y mostrarla junto al input de cantidad
al seleccionar el ingrediente.

### 1.10 Colores únicos por estado

Las clases ya existen en `static/css/styles.css` (`badge-pendiente`,
`card-preparacion`, etc.). Falta aplicarlas de forma consistente.

| Estado | Color |
|---|---|
| Pendiente | Amarillo |
| En preparación | Turquesa |
| En camino | Naranja |
| Entregado | Verde |
| Cancelado | Rojo |

El botón de avanzar estado hoy es siempre `btn-success` (verde). Debe tomar el
color del **estado destino**, tanto en la cola como en el detalle.

### 1.11 Botón "Ver Detalle" proporcional

**Archivo:** `templates/orders/order_queue.html`, bloque `.order-actions`

Igualar el ancho con el botón de cambiar estado.

### 1.12 Barras de búsqueda a ancho completo

- **Cola de pedidos** (`order_queue.html`): 3 elementos — input de búsqueda,
  select de estados, botón filtrar.
- **Historial** (`order_history.html`): 5 elementos.

Ambas dentro de `.filter-bar`. Trabajo de CSS.

---

## TANDA 2 — Modelo de Clientes

Es el ítem más grande de la lista y merece su propia tanda.

### Situación actual

`Order` guarda los datos del cliente como texto suelto:
`cliente_nombre`, `cliente_telefono`, `cliente_direccion`. No existe un modelo
`Cliente`.

### Trabajo

1. Crear el modelo `Cliente` (nombre, teléfono, dirección, fecha de alta).
2. Agregar FK opcional `cliente` en `Order`, manteniendo los campos de texto
   para no romper los pedidos históricos.
3. Migración de datos: crear clientes a partir de los pedidos existentes,
   agrupando por teléfono.
4. En Nuevo Pedido: buscador por teléfono o nombre que autocomplete los tres
   campos, más la opción "cliente nuevo".
5. Decidir si al crear un pedido con datos que no coinciden con ningún cliente
   se da de alta uno automáticamente.

---

## TANDA 3 — Eliminar pedido, forzar stock y limpieza de recetas

Depende de las decisiones #2 y #3.

### 3.1 Eliminar pedido desde "Ver Detalle"

Botón nuevo en `order_detail.html` que pregunte si se devuelve el stock al
inventario antes de eliminar.

**Cuidado con el orden:** `devolver_stock()` filtra los movimientos por
`pedido_relacionado=order`. Hay que devolver el stock **antes** de eliminar el
pedido, o se pierde la referencia.

A favor: `InventoryMovement.pedido_relacionado` está definido con
`on_delete=SET_NULL`, así que los movimientos sobreviven como registro histórico
aunque el pedido desaparezca.

### 3.2 Forzar avance con stock insuficiente

**Archivo:** `apps/orders/services.py` → `descontar_stock()`

La función hace dos pasadas: primero valida todo el pedido, después descuenta.
Agregar un parámetro `forzar=False` que saltee la validación.

En la interfaz: cuando aparece el mensaje de stock insuficiente, ofrecer
"Continuar de todos modos" en lugar de solo bloquear.

Aplicar la decisión #2 para el tratamiento del stock resultante.

### 3.3 Quitar "Adicional" de la pestaña Recetas

1. Quitar el selector de tipo en `templates/inventory/recipes.html`.
2. Quitar `addons` del contexto en `apps/inventory/views.py` → `recipes()`.
3. Decidir qué hacer con las filas existentes que tengan
   `producto_tipo='addon'` (limpiarlas o dejarlas inertes).

Ver BUG-3: esas recetas nunca funcionaron.

---

## FUERA DE ESTE PLAN

Sigue pendiente de antes y no se toca en estas tres tandas:

- Reemplazar los mocks de `static/js/mocks/` por datos reales del backend.
- Implementar la app `reports` (hoy es una cáscara vacía, sin migraciones).
- Implementar la app `costs` (ídem).
- Módulo "Cerrar el Día" — ver `Idea_CierreDelDia.md`.
