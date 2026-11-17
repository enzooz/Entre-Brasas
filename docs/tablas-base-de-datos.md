# Tablas de la base de datos — Entre Brasas

Motor: **SQLite** (archivo `app/db.sqlite3`). Las tablas se definen en los
`models.py` de cada app y las crea `manage.py migrate`.

La base tiene **15 tablas**:

- **12 del sistema**, en cuatro apps: `menu`, `inventario`, `pedidos` y `config`.
- **3 internas de Django**: `django_migrations`, `django_content_type` y `django_session`.

Las apps `reportes` y `costos` **no tienen tablas propias**: calculan todo
leyendo las tablas de pedidos, menú e inventario.

Todas las tablas tienen una columna `id`, que es la clave primaria (un entero
autoincremental). No se repite abajo.

---

## Cómo se relacionan

```
MENÚ
  menu_hamburguesa ──< menu_adicional_hamburguesas >── menu_adicional

RECETAS Y STOCK
  menu_hamburguesa       ──< inventario_receta
  menu_adicional         ──< inventario_receta
  inventario_ingrediente ──< inventario_receta
  inventario_ingrediente ──< inventario_movimientoinventario
  pedidos_pedido         ──< inventario_movimientoinventario   (opcional)

PEDIDOS
  pedidos_cliente   ──< pedidos_pedido                         (opcional)
  pedidos_pedido    ──< pedidos_itempedido
  menu_hamburguesa  ──< pedidos_itempedido
  pedidos_itempedido ──< pedidos_adicionaldeitem
  menu_adicional     ──< pedidos_adicionaldeitem
  pedidos_pedido    ──< pedidos_historialestado

CONFIGURACIÓN
  config_configuracion   (sin relaciones, una sola fila)
```

`A ──< B` significa "un A tiene muchos B": B guarda la clave foránea (FK) que
apunta a A. "Opcional" quiere decir que esa FK puede quedar vacía.

---

## App `menu`: qué vende el local

### `menu_hamburguesa`

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `nombre` | texto (100), **único** | Sí | Nombre de la hamburguesa |
| `descripcion` | texto largo | Sí | Descripción para el menú |
| `precio` | entero ≥ 0 | Sí | Precio en pesos, sin centavos |
| `incluye_papas` | sí/no | Sí (por defecto sí) | Si viene con papas |
| `activa` | sí/no | Sí (por defecto sí) | En vez de borrarla, se desactiva |

### `menu_adicional`

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `nombre` | texto (100), **único** | Sí | Nombre del extra (bacon, huevo...) |
| `precio` | entero ≥ 0 | Sí | Precio en pesos |
| `activo` | sí/no | Sí (por defecto sí) | En vez de borrarlo, se desactiva |
| `es_medallon_extra` | sí/no | Sí (por defecto no) | Marca el adicional que hace a la hamburguesa doble o triple |

### `menu_adicional_hamburguesas` (tabla intermedia)

Relación **muchos a muchos**: qué adicional se puede pedir en qué hamburguesa.
No tiene modelo propio. Django la crea sola a partir del campo
`Adicional.hamburguesas`.

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `adicional_id` | FK → `menu_adicional` | Sí | El adicional |
| `hamburguesa_id` | FK → `menu_hamburguesa` | Sí | La hamburguesa donde se ofrece |

El par (`adicional_id`, `hamburguesa_id`) es **único**: el mismo vínculo no se
puede repetir.

---

## App `inventario`: insumos y stock

### `inventario_ingrediente`

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `nombre` | texto (100), **único** | Sí | Nombre del insumo |
| `stock_actual` | decimal (10 dígitos, 2 decimales) | Sí (por defecto 0) | Cuánto hay. **Puede quedar negativo**: el sistema nunca frena un pedido por falta de stock, solo avisa |
| `unidad` | texto (10) | Sí | Una de: `kg`, `g`, `L`, `mL`, `unidades` |
| `stock_minimo` | decimal (10, 2) | Sí | Debajo de este valor se avisa que hay que reponer |
| `precio_compra` | entero ≥ 0 | Sí (por defecto 0) | Precio de la última compra, por unidad. Se usa para los costos |
| `activo` | sí/no | Sí (por defecto sí) | En vez de borrarlo, se desactiva |

### `inventario_receta`

Cada fila es **una línea de receta**: "tal producto lleva tanto de tal
ingrediente". La receta completa de un producto son varias filas.

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `hamburguesa_id` | FK → `menu_hamburguesa` | No | La hamburguesa, si la receta es de una hamburguesa |
| `adicional_id` | FK → `menu_adicional` | No | El adicional, si la receta es de un adicional |
| `ingrediente_id` | FK → `inventario_ingrediente` | Sí | El insumo |
| `cantidad_requerida` | decimal (10, 2) | Sí | Cuánto lleva **una unidad** del producto |

Una receta es de una hamburguesa **o** de un adicional, nunca de los dos. Por
eso esas dos columnas aceptan vacío (NULL). La base no lo controla con una
restricción: lo respeta el código que carga las recetas.

### `inventario_movimientoinventario`

El historial de **todas** las entradas y salidas de stock. **No se edita ni
se borra**: para revertir algo se carga el movimiento contrario.

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `ingrediente_id` | FK → `inventario_ingrediente` | Sí | Qué insumo se movió |
| `tipo` | texto (10) | Sí | `entrada` o `salida` |
| `cantidad` | decimal (10, 2) | Sí | Cuánto se movió |
| `motivo` | texto (255) | Sí | Por qué (compra, pedido, pérdida, conteo...) |
| `precio_unitario` | entero ≥ 0 | Sí (por defecto 0) | Precio pagado por unidad, solo en compras |
| `fecha` | fecha y hora | Sí (automática) | Cuándo se registró |
| `pedido_relacionado_id` | FK → `pedidos_pedido` | No | El pedido que lo generó, si lo generó un pedido |

El **conteo** (cargar lo que se contó en la cocina) no es un tipo aparte. Se
calcula la diferencia con el stock del sistema y se guarda como una entrada o
una salida, con el motivo "Conteo: había X, se contaron Y".

---

## App `pedidos`: clientes y pedidos

### `pedidos_cliente`

Los clientes guardados, para no volver a escribir sus datos.

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `nombre` | texto (200) | Sí | Nombre |
| `telefono` | texto (50) | Puede quedar vacío | Teléfono tal como se escribió |
| `telefono_clave` | texto (20), **único** | No | Solo los dígitos del teléfono. Identifica al cliente sin duplicarlo |
| `direccion` | texto (300) | Puede quedar vacío | Última dirección usada |
| `fecha_alta` | fecha y hora | Sí (automática) | Cuándo se creó |
| `fecha_actualizacion` | fecha y hora | Sí (automática) | Última vez que se modificó |

### `pedidos_pedido`

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `cliente_id` | FK → `pedidos_cliente` | No | El cliente guardado al que pertenece |
| `cliente_nombre` | texto (200) | Sí | **Copia** del nombre al momento del pedido |
| `cliente_telefono` | texto (50) | Sí | **Copia** del teléfono |
| `cliente_direccion` | texto (300) | Sí | **Copia** de la dirección |
| `observaciones` | texto largo | No | Notas del pedido |
| `metodo_pago` | texto (20) | Sí | `efectivo` o `transferencia` |
| `distancia_km` | decimal (5, 2) | Sí (por defecto 0) | Distancia del envío |
| `costo_envio` | entero ≥ 0 | Sí (por defecto 0) | Lo que se cobró de envío |
| `retiro_local` | sí/no | Sí (por defecto no) | Si lo retira en el local (envío $0) |
| `total` | entero ≥ 0 | Sí | Total cobrado, calculado al crear el pedido |
| `estado` | texto (20) | Sí (por defecto `pendiente`) | `pendiente`, `en_preparacion`, `en_camino`, `entregado` o `cancelado` |
| `fecha_creacion` | fecha y hora | Sí (automática) | Cuándo se cargó |

### `pedidos_itempedido`

Cada hamburguesa pedida dentro de un pedido.

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `pedido_id` | FK → `pedidos_pedido` | Sí | A qué pedido pertenece |
| `hamburguesa_id` | FK → `menu_hamburguesa` | Sí | Qué hamburguesa |
| `cantidad` | entero ≥ 0 | Sí (por defecto 1) | Cuántas |
| `precio_unitario` | entero ≥ 0 | Sí | **Copia** del precio al momento de la venta |
| `nota` | texto (200) | Puede quedar vacío | Pedido especial para la cocina ("sin cebolla") |

### `pedidos_adicionaldeitem`

Cada extra aplicado a una hamburguesa pedida.

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `item_id` | FK → `pedidos_itempedido` | Sí | A qué hamburguesa del pedido |
| `adicional_id` | FK → `menu_adicional` | Sí | Qué adicional |
| `precio` | entero ≥ 0 | Sí | **Copia** del precio al momento de la venta |

### `pedidos_historialestado`

Cada cambio de estado de un pedido.

| Columna | Tipo | Obligatorio | Qué guarda |
|---|---|---|---|
| `pedido_id` | FK → `pedidos_pedido` | Sí | Qué pedido |
| `estado_anterior` | texto (20) | Sí | Estado de antes |
| `estado_nuevo` | texto (20) | Sí | Estado nuevo |
| `observacion` | texto largo | No | Por ejemplo, el motivo de una cancelación |
| `fecha` | fecha y hora | Sí (automática) | Cuándo cambió |

---

## App `config`: parámetros del sistema

### `config_configuracion`

Tiene **una sola fila** (`id = 1`). Si no existe, el sistema la crea con los
valores por defecto.

| Columna | Tipo | Por defecto | Qué guarda |
|---|---|---|---|
| `tarifa_100m` | decimal (10, 2) | 50 | Precio por cada 100 m de envío después de la distancia incluida |
| `distancia_minima` | decimal (5, 2) | 1 | Kilómetros que cubre el envío mínimo |
| `costo_minimo_envio` | entero ≥ 0 | 1000 | Precio del envío mínimo |
| `costo_hora_mano_obra` | entero ≥ 0 | 2500 | Costo de una hora de trabajo, para los costos |
| `whatsapp_cocina` | texto (30) | vacío | Número de WhatsApp de la cocina |
| `geoapify_api_key` | texto (128) | vacío | Clave del servicio de mapas |
| `local_latitud` | número real | -27.455266 | Ubicación del local en el mapa |
| `local_longitud` | número real | -58.992536 | Ubicación del local en el mapa |

---

## Tablas internas de Django

No las escribimos nosotros. Las crea Django.

| Tabla | Para qué |
|---|---|
| `django_migrations` | Registra qué migraciones ya se aplicaron a esta base |
| `django_content_type` | Lista de los modelos del proyecto; Django la usa internamente |
| `django_session` | Sesiones del navegador. Viene con Django; el sistema no guarda datos propios ahí y normalmente está vacía |

No hay tablas de usuarios (`auth_*`): el sistema no tiene login porque lo usa
una sola persona en la compu del local.

---

## Decisiones que se ven en las tablas

- **Precios en enteros de pesos**, sin centavos. Los precios del rubro son redondos.
- **Los precios se copian al pedido** (`precio_unitario`, `precio`). Si mañana
  sube una hamburguesa, los pedidos viejos siguen mostrando lo que se cobró.
- **Los datos del cliente también se copian al pedido.** Si se actualiza el
  cliente, las ventas anteriores no cambian.
- **Nada se borra, se desactiva** (`activa`, `activo`). Si se borrara una
  hamburguesa, los pedidos que la incluyen quedarían rotos.
- **El stock tiene historial completo.** `stock_actual` es el saldo y
  `inventario_movimientoinventario` explica cada cambio.
- **El stock se descuenta cuando el pedido pasa a "en preparación"**, según la
  receta de cada hamburguesa y adicional. Recién cuando llega a "entregado"
  cuenta como venta en los reportes.
