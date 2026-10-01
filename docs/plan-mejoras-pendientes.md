# PLAN DE MEJORAS PENDIENTES — ENTRE BRASAS

**Última actualización:** 30/09/2026
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
| Nuevo pedido | Adicionales por cada producto | ✅ Hecho (bug B-1 resuelto el 27/09) |
| Nuevo pedido | Carga rápida + comanda para cocina por WhatsApp | ✅ Hecho (27/09) |
| Nuevo pedido | Pegar el mensaje de WhatsApp y completar solo | ✅ Hecho (28/09) |
| Nuevo pedido | Ocultar "Distancia" si retira en el local | ✅ Hecho |
| Nuevo pedido | Mostrar el total antes de confirmar | ✅ Hecho |
| Nuevo pedido | Conservar lo escrito al salir o recargar | ✅ Hecho: borrador por pestaña con sessionStorage |
| Nuevo pedido | Clientes guardados y búsqueda por nombre o teléfono | ✅ Hecho: Tanda 3 |
| Cola | Un color por estado (etiqueta, tarjeta y botón) | ✅ Hecho |
| Cola | "Ver detalle" del mismo tamaño que el botón de estado | ✅ Hecho |
| Cola | Barra de búsqueda a ancho completo | ✅ Hecho |
| Cola | Seguir aunque falte stock | ✅ Hecho (28/09): nunca frena, avisa |
| Historial | Barra de búsqueda a ancho completo | ✅ Hecho |
| Historial | Cambios de estado con fecha y hora | ✅ Hecho |
| Historial | Botón "Eliminar pedido" | ❓ A decidir (#3) |
| Inventario | Unidad de medida al registrar movimiento | ✅ Hecho |
| Inventario | Regla para desactivar ingredientes | ✅ Hecho: solo bloquean recetas de productos activos |
| Recetas | Quitar la opción "Adicional" | ❓ A decidir (#4) — no se recomienda |

---

## DECISIONES PENDIENTES

### 1. Regla para desactivar ingredientes

**Implementado:** se permite desactivar aunque existan compras, consumos o ajustes.
No se borran el ingrediente, su stock, sus recetas ni sus movimientos.
Solo se bloquea la baja si está en la receta de una hamburguesa activa o de un
adicional activo (aunque ese adicional todavía no esté asociado a hamburguesas).
La pantalla explica que primero hay que quitarlo de esas recetas o desactivar
los productos. Ver `app/inventario/views.py` → `activar_ingrediente()`.

### 2. Qué pasa con el stock al seguir sin stock suficiente

- **Opción A — stock negativo:** refleja la realidad y el inventario avisa que hay que corregirlo.
- **Opción B — dejarlo en 0:** más prolijo, pero se pierde la señal.

**Recomendación:** A.
**Decisión:** ✅ **A — stock negativo** (28/09/2026). Además, los pedidos nunca
se frenan por stock: solo se avisa. Ver Tanda 2.

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

El menú real ya incluye recetas de adicionales. Las cantidades que no provienen
de la captura del menú son estimaciones; su revisión con el local está pospuesta
por decisión del usuario el 30/09. Tener stock en 0 no confirma una receta.

**Recomendación:** mantenerla y cargar las recetas de los adicionales.

**Decisión:** _pendiente_

---

## BUGS CONOCIDOS

### B-1 — Dos filas con la misma hamburguesa mezclan los adicionales ✅ Resuelto

Los campos del formulario se nombraban con el id de la hamburguesa
(`adicionales_3[]`), así que dos filas de la misma hamburguesa compartían los
adicionales. Desde el 27/09/2026 todos los campos van por número de fila
(`hamburguesa_0`, `adicionales_0[]`, etc.). Ver `crear_items_del_pedido()`.

---

## TANDA 1 — Cambios chicos ✅ Hecho

1. **Borrador en Nuevo pedido:** sessionStorage conserva datos, unidades, extras,
   notas, entrega, pago y cliente elegido al salir o recargar en la misma pestaña.
   Se limpia tras creación confirmada o descarte explícito, no al enviar.
   Cerrar la pestaña termina la sesión; no se comparte entre pestañas.
2. **Regla de ingredientes:** aplicada la decisión #1, preservando historial.
3. **Campos numéricos:** sin flechas visuales, conservando min, max, step y validación.

## TANDA 2 — Seguir aunque falte stock ✅ Hecho (28/09/2026)

En vez de ofrecer "Continuar de todos modos", se decidió que el stock **nunca
frene** un pedido: si la hamburguesa se está haciendo, los ingredientes están
en la cocina aunque el sistema no lo sepa. Motivo: el local no va a cargar el
inventario real el día que instala, y se descartó arrancar con 999 de stock
porque los medallones se terminan en pocos días y vuelve a frenar.

- `descontar_stock()` (`app/pedidos/calculos.py`) descuenta siempre y el stock
  puede quedar negativo. Devuelve los ingredientes que **recién** pasaron a
  negativo, y la cola muestra un aviso una sola vez por ingrediente.
- **Stock inicial en 0** (`seed_data`): nada de números inventados.
- **Conteo** en Inventario → Registrar movimiento: se escribe lo que hay de
  verdad y el sistema guarda la diferencia como entrada o salida, con el
  motivo "Conteo: había X, se contaron Y".
- Inventario avisa qué ingredientes están en 0 o en negativo (todavía sin
  contar) y muestra los negativos en rojo.
- De paso se arregló que el precio de "Registrar movimiento" era obligatorio
  aunque la pantalla decía "opcional".

## TANDA 3 — Clientes ✅ Hecho

1. Modelo `pedidos.Cliente`: nombre, teléfono, dirección, fechas de alta y actualización.
2. `Pedido.cliente` opcional, con SET_NULL; mantiene los campos de texto y precios
   del momento de la venta. Actualizar un cliente no reescribe pedidos anteriores.
3. Migraciones 0004 y 0005: importan pedidos existentes por teléfono de 7–20
   dígitos; ignoran separadores, sin inferir país o prefijos. Los pedidos sin un
   teléfono identificable no se fusionan por nombre. Se conserva su contenido.
4. Búsqueda local por nombre o teléfono en Nuevo pedido; hasta 8 resultados,
   sin caché. Elegir uno completa nombre, teléfono y dirección, sin crear pedidos.
   Si cambia la dirección se limpia la distancia para volver a calcularla.
5. Crear un pedido guarda/actualiza su cliente en la misma transacción. Sin
   teléfono, solo se reutiliza un cliente elegido explícitamente; no se unen
   homónimos. Cliente nuevo limpia sus campos, no las hamburguesas ni notas.
6. La selección se conserva en el borrador. Un error al crear no guarda un
   cliente parcial ni borra el borrador.

## ENTREGA Y VERIFICACIONES

- Prueba aislada del instalador: `app/entre_brasas/probar_instalacion.py`.
  Ejecuta instalación limpia y actualización en una carpeta temporal, sin usar
  la base ni el escritorio real. Comprueba menú, stock inicial 0, acceso directo
  a pythonw y conservación de pedidos, clientes, precios, tarifas y respaldo.
- Pruebas del iniciador: arranque sin consola, doble apertura, apagado desde la
  web y reapertura sin pérdida de pedidos (`test_servidor_local.py`).
- La comprobación en la computadora final del local requiere acceso a esa PC;
  una prueba aislada en desarrollo no sustituye esa aceptación.
- Cantidades de recetas: **pospuestas por el usuario**. Stock actual sin cambios;
  el local podrá cargar las existencias mediante Registrar movimiento → Conteo.

---

## HECHO EL 27/09/2026 — Carga rápida y comanda para cocina

Nota histórica: las cantidades agrupadas y nombres Simple/Doble/Triple descritos
abajo fueron reemplazados el 30/09 por unidades independientes y cantidades
explícitas de medallones extra. Ver `cambios-menu-envio-personalizacion.md`.

En el local los pedidos llegan por WhatsApp y el que está en la PC se los
reenvía a la cocina con un WhatsApp escrito a mano. Ahora el pedido se carga
una sola vez y el sistema arma ese mensaje solo.

- **Nuevo pedido más rápido:** un botón por hamburguesa, cantidad con − / +,
  selector Simple / Doble / Triple (el doble es el adicional marcado como
  "medallón extra"), adicionales como etiquetas y una nota por hamburguesa
  ("dip de alioli"). Si retira, alcanza con el nombre; dirección (o link de
  Maps), teléfono y km se piden solo para envío.
- **Comanda** (`app/pedidos/comanda.py`): el texto con el mismo formato que
  usaba el local ("1 Crispy doble", "RETIRA", y para los envíos dirección,
  teléfono, pago y total).
- **Enviar a cocina:** al crear el pedido se abre el detalle con la comanda y
  los botones "Enviar a cocina por WhatsApp" (si se cargó el número en
  Configuración) y "Copiar". La cola tiene "Copiar comanda" en cada tarjeta.
- **Datos nuevos:** `ItemPedido.nota`, `Adicional.es_medallon_extra` y
  `Configuracion.whatsapp_cocina` (migraciones `pedidos/0003`, `menu/0002`,
  `config/0002`).
- **Pegar mensaje de WhatsApp (28/09/2026):** arriba de Nuevo pedido hay una
  caja para pegar el mensaje del cliente. `app/pedidos/interpretar.py` lo lee
  renglón por renglón y completa el formulario: hamburguesas aunque estén mal
  escritas ("crispi", "tradicional"), cantidades ("2", "dos", "x2"),
  doble/triple, adicionales ("con panceta"), notas ("sin cebolla"), retira o
  envío, link de Maps o dirección escrita, teléfono, forma de pago y nombre
  (también el del contacto si se copió desde WhatsApp Web). Lo que no entiende
  queda en Observaciones y se avisa. No guarda nada: siempre se revisa y se
  toca "Crear pedido".

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
