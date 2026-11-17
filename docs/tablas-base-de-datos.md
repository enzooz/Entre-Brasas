# Tablas de la base de datos — Entre Brasas

Motor: **SQLite** (archivo `app/db.sqlite3`). Las tablas se definen en los
`models.py` de cada app y las crea `manage.py migrate`.

La base tiene **15 tablas**:

- **12 del sistema**, en cuatro apps: `menu`, `inventario`, `pedidos` y `config`.
- **3 internas de Django**: `django_migrations`, `django_content_type` y `django_session`.

Las apps `reportes` y `costos` **no tienen tablas propias**: calculan todo
leyendo las tablas de pedidos, menú e inventario.

---

## Cómo leer las tablas

Cada tabla tiene estas columnas:

- **Tipo Django:** el campo tal como está en `models.py` (por ejemplo `CharField(200)`).
- **Tipo SQL:** cómo quedó declarada la columna en SQLite, sacado del
  `CREATE TABLE` real de la base (por ejemplo `varchar(200)`).
- **Restricciones:** las reglas que controla la propia base:
  - `PK`: clave primaria. Todas las tablas tienen `id`, un entero autoincremental.
  - `NOT NULL`: no puede quedar vacía. `NULL` quiere decir que sí puede.
  - `UNIQUE`: no se puede repetir el valor.
  - `CHECK ≥ 0`: no acepta números negativos.
  - `FK → tabla`: clave foránea que apunta al `id` de esa tabla.
- **Descripción:** qué guarda. Los valores **por defecto** también figuran
  ahí; esos los completa Django al guardar, no la base.

En SQLite los `bool` se guardan como `0` o `1`, y los `datetime` como texto con
fecha y hora.

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

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `nombre` | `CharField(100)` | `varchar(100)` | NOT NULL, UNIQUE | Nombre de la hamburguesa |
| `descripcion` | `TextField` | `text` | NOT NULL | Descripción para el menú |
| `precio` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Precio en pesos, sin centavos |
| `incluye_papas` | `BooleanField` | `bool` | NOT NULL | Si viene con papas. Por defecto sí |
| `activa` | `BooleanField` | `bool` | NOT NULL | En vez de borrarla, se desactiva. Por defecto sí |

### `menu_adicional`

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `nombre` | `CharField(100)` | `varchar(100)` | NOT NULL, UNIQUE | Nombre del extra (bacon, huevo...) |
| `precio` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Precio en pesos |
| `activo` | `BooleanField` | `bool` | NOT NULL | En vez de borrarlo, se desactiva. Por defecto sí |
| `es_medallon_extra` | `BooleanField` | `bool` | NOT NULL | Marca el adicional que hace a la hamburguesa doble o triple. Por defecto no |

### `menu_adicional_hamburguesas` (tabla intermedia)

Relación **muchos a muchos**: qué adicional se puede pedir en qué hamburguesa.
No tiene modelo propio. Django la crea sola a partir del campo
`hamburguesas = ManyToManyField(Hamburguesa)` del modelo `Adicional`.

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | (automático) | `integer` | PK, autoincremental | Identificador |
| `adicional_id` | (automático) | `bigint` | NOT NULL, FK → `menu_adicional` | El adicional |
| `hamburguesa_id` | (automático) | `bigint` | NOT NULL, FK → `menu_hamburguesa` | La hamburguesa donde se ofrece |

El par (`adicional_id`, `hamburguesa_id`) es **UNIQUE**: el mismo vínculo no se
puede repetir.

---

## App `inventario`: insumos y stock

### `inventario_ingrediente`

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `nombre` | `CharField(100)` | `varchar(100)` | NOT NULL, UNIQUE | Nombre del insumo |
| `stock_actual` | `DecimalField(10,2)` | `decimal` | NOT NULL | Cuánto hay. Por defecto 0. **Puede quedar negativo**: el sistema nunca frena un pedido por falta de stock, solo avisa |
| `unidad` | `CharField(10)` | `varchar(10)` | NOT NULL | Una de: `kg`, `g`, `L`, `mL`, `unidades` |
| `stock_minimo` | `DecimalField(10,2)` | `decimal` | NOT NULL | Debajo de este valor se avisa que hay que reponer |
| `precio_compra` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Precio de la última compra, por unidad. Se usa para los costos. Por defecto 0 |
| `activo` | `BooleanField` | `bool` | NOT NULL | En vez de borrarlo, se desactiva. Por defecto sí |

`DecimalField(10,2)` significa hasta 10 dígitos en total, 2 de ellos decimales.

### `inventario_receta`

Cada fila es **una línea de receta**: "tal producto lleva tanto de tal
ingrediente". La receta completa de un producto son varias filas.

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `hamburguesa_id` | `ForeignKey(Hamburguesa)` | `bigint` | NULL, FK → `menu_hamburguesa` | La hamburguesa, si la receta es de una hamburguesa |
| `adicional_id` | `ForeignKey(Adicional)` | `bigint` | NULL, FK → `menu_adicional` | El adicional, si la receta es de un adicional |
| `ingrediente_id` | `ForeignKey(Ingrediente)` | `bigint` | NOT NULL, FK → `inventario_ingrediente` | El insumo |
| `cantidad_requerida` | `DecimalField(10,2)` | `decimal` | NOT NULL | Cuánto lleva **una unidad** del producto |

Una receta es de una hamburguesa **o** de un adicional, nunca de los dos. Por
eso esas dos columnas aceptan NULL. La base no lo controla con una
restricción: lo respeta el código que carga las recetas.

### `inventario_movimientoinventario`

El historial de **todas** las entradas y salidas de stock. **No se edita ni
se borra**: para revertir algo se carga el movimiento contrario.

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `ingrediente_id` | `ForeignKey(Ingrediente)` | `bigint` | NOT NULL, FK → `inventario_ingrediente` | Qué insumo se movió |
| `tipo` | `CharField(10)` | `varchar(10)` | NOT NULL | `entrada` o `salida` |
| `cantidad` | `DecimalField(10,2)` | `decimal` | NOT NULL | Cuánto se movió |
| `motivo` | `CharField(255)` | `varchar(255)` | NOT NULL | Por qué (compra, pedido, pérdida, conteo...) |
| `precio_unitario` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Precio pagado por unidad, solo en compras. Por defecto 0 |
| `fecha` | `DateTimeField(auto_now_add)` | `datetime` | NOT NULL | Cuándo se registró. La pone Django sola al crear la fila |
| `pedido_relacionado_id` | `ForeignKey(Pedido)` | `bigint` | NULL, FK → `pedidos_pedido` | El pedido que lo generó, si lo generó un pedido |

El **conteo** (cargar lo que se contó en la cocina) no es un tipo aparte. Se
calcula la diferencia con el stock del sistema y se guarda como una entrada o
una salida, con el motivo "Conteo: había X, se contaron Y".

---

## App `pedidos`: clientes y pedidos

### `pedidos_cliente`

Los clientes guardados, para no volver a escribir sus datos.

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `nombre` | `CharField(200)` | `varchar(200)` | NOT NULL | Nombre |
| `telefono` | `CharField(50)` | `varchar(50)` | NOT NULL | Teléfono tal como se escribió. Puede ser texto vacío |
| `telefono_clave` | `CharField(20)` | `varchar(20)` | NULL, UNIQUE | Solo los dígitos del teléfono. Identifica al cliente sin duplicarlo |
| `direccion` | `CharField(300)` | `varchar(300)` | NOT NULL | Última dirección usada. Puede ser texto vacío |
| `fecha_alta` | `DateTimeField(auto_now_add)` | `datetime` | NOT NULL | Cuándo se creó. La pone Django |
| `fecha_actualizacion` | `DateTimeField(auto_now)` | `datetime` | NOT NULL | Última vez que se modificó. La actualiza Django en cada guardado |

### `pedidos_pedido`

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Número de pedido |
| `cliente_id` | `ForeignKey(Cliente)` | `bigint` | NULL, FK → `pedidos_cliente` | El cliente guardado al que pertenece |
| `cliente_nombre` | `CharField(200)` | `varchar(200)` | NOT NULL | **Copia** del nombre al momento del pedido |
| `cliente_telefono` | `CharField(50)` | `varchar(50)` | NOT NULL | **Copia** del teléfono |
| `cliente_direccion` | `CharField(300)` | `varchar(300)` | NOT NULL | **Copia** de la dirección |
| `observaciones` | `TextField` | `text` | NULL | Notas del pedido |
| `metodo_pago` | `CharField(20)` | `varchar(20)` | NOT NULL | `efectivo` o `transferencia` |
| `distancia_km` | `DecimalField(5,2)` | `decimal` | NOT NULL | Distancia del envío. Por defecto 0 |
| `costo_envio` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Lo que se cobró de envío. Por defecto 0 |
| `retiro_local` | `BooleanField` | `bool` | NOT NULL | Si lo retira en el local (envío $0). Por defecto no |
| `total` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Total cobrado, calculado al crear el pedido |
| `estado` | `CharField(20)` | `varchar(20)` | NOT NULL | `pendiente`, `en_preparacion`, `en_camino`, `entregado` o `cancelado`. Por defecto `pendiente` |
| `fecha_creacion` | `DateTimeField(auto_now_add)` | `datetime` | NOT NULL | Cuándo se cargó. La pone Django |

### `pedidos_itempedido`

Cada hamburguesa pedida dentro de un pedido.

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `pedido_id` | `ForeignKey(Pedido)` | `bigint` | NOT NULL, FK → `pedidos_pedido` | A qué pedido pertenece |
| `hamburguesa_id` | `ForeignKey(Hamburguesa)` | `bigint` | NOT NULL, FK → `menu_hamburguesa` | Qué hamburguesa |
| `cantidad` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Cuántas. Por defecto 1 |
| `precio_unitario` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | **Copia** del precio al momento de la venta |
| `nota` | `CharField(200)` | `varchar(200)` | NOT NULL | Pedido especial para la cocina ("sin cebolla"). Puede ser texto vacío |

### `pedidos_adicionaldeitem`

Cada extra aplicado a una hamburguesa pedida.

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `item_id` | `ForeignKey(ItemPedido)` | `bigint` | NOT NULL, FK → `pedidos_itempedido` | A qué hamburguesa del pedido |
| `adicional_id` | `ForeignKey(Adicional)` | `bigint` | NOT NULL, FK → `menu_adicional` | Qué adicional |
| `precio` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | **Copia** del precio al momento de la venta |

### `pedidos_historialestado`

Cada cambio de estado de un pedido.

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Identificador |
| `pedido_id` | `ForeignKey(Pedido)` | `bigint` | NOT NULL, FK → `pedidos_pedido` | Qué pedido |
| `estado_anterior` | `CharField(20)` | `varchar(20)` | NOT NULL | Estado de antes (mismos valores que `pedidos_pedido.estado`) |
| `estado_nuevo` | `CharField(20)` | `varchar(20)` | NOT NULL | Estado nuevo |
| `observacion` | `TextField` | `text` | NULL | Por ejemplo, el motivo de una cancelación |
| `fecha` | `DateTimeField(auto_now_add)` | `datetime` | NOT NULL | Cuándo cambió. La pone Django |

---

## App `config`: parámetros del sistema

### `config_configuracion`

Tiene **una sola fila** (`id = 1`). Si no existe, el sistema la crea con los
valores por defecto.

| Columna | Tipo Django | Tipo SQL | Restricciones | Descripción |
|---|---|---|---|---|
| `id` | `BigAutoField` | `integer` | PK, autoincremental | Siempre 1 |
| `tarifa_100m` | `DecimalField(10,2)` | `decimal` | NOT NULL | Precio por cada 100 m de envío después de la distancia incluida. Por defecto 50 |
| `distancia_minima` | `DecimalField(5,2)` | `decimal` | NOT NULL | Kilómetros que cubre el envío mínimo. Por defecto 1 |
| `costo_minimo_envio` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Precio del envío mínimo. Por defecto 1000 |
| `costo_hora_mano_obra` | `PositiveIntegerField` | `integer unsigned` | NOT NULL, CHECK ≥ 0 | Costo de una hora de trabajo, para los costos. Por defecto 2500 |
| `whatsapp_cocina` | `CharField(30)` | `varchar(30)` | NOT NULL | Número de WhatsApp de la cocina. Puede ser texto vacío |
| `geoapify_api_key` | `CharField(128)` | `varchar(128)` | NOT NULL | Clave del servicio de mapas. Puede ser texto vacío |
| `local_latitud` | `FloatField` | `real` | NOT NULL | Ubicación del local en el mapa. Por defecto -27.455266 |
| `local_longitud` | `FloatField` | `real` | NOT NULL | Ubicación del local en el mapa. Por defecto -58.992536 |

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
