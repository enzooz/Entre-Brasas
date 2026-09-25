# RESUMEN DE LA BASE DE DATOS — ENTRE BRASAS

**Fecha del relevamiento:** 11/09/2026
**Estado de la base al momento de revisarla:** última escritura el 24/08/2026 16:43

---

## ¿Qué motor usamos?

**SQLite 3.** Es una base de datos que vive en **un solo archivo**. No hay un
servidor de base de datos corriendo aparte: SQLite es una librería que va
embebida dentro del proceso de Django. No hay nada que "prender", ni puerto que
escuchar, ni usuario y contraseña de base.

El proyecto también está preparado para **PostgreSQL**, como opción. En
`entre_brasas/settings.py` hay un condicional:

- Si existe la variable de entorno `DATABASE_URL` → usa PostgreSQL.
- Si no existe → usa SQLite.

Hoy corre en SQLite. PostgreSQL nunca se usó en la práctica.

---

## ¿Dónde está el archivo?

```
C:\Users\nikov\Desktop\Entre Brasas\app\db.sqlite3
```

| Dato | Valor |
|---|---|
| Tamaño | 240 KB (60 páginas de 4 KB) |
| Encoding | UTF-8 |
| Journal mode | `delete` (el default de SQLite) |

**No está versionada en git.** El `.gitignore` incluye `*.sqlite3`, así que estos
datos son locales de esta máquina. Nadie más del equipo los tiene.

Consecuencia práctica: si otra persona clona el repo, arranca con la base vacía y
tiene que correr `migrate` + `seed_data`.

---

## ¿Cómo se corre?

La base no se corre por separado. Se levanta junto con Django:

```bat
cd "C:\Users\nikov\Desktop\Entre Brasas\app"
venv\Scripts\activate
python manage.py runserver
```

Comandos que operan sobre la base:

| Comando | Qué hace |
|---|---|
| `python manage.py migrate` | Aplica las migraciones pendientes |
| `python manage.py showmigrations` | Muestra cuáles están aplicadas |
| `python manage.py makemigrations` | Genera una migración nueva tras cambiar un modelo |
| `python manage.py dbshell` | Abre una consola SQL directa |
| `python manage.py shell` | Abre una consola Python con los modelos cargados |
| `python manage.py seed_data` | Carga los datos iniciales de prueba |

Para empezar de cero: borrar `db.sqlite3`, correr `migrate` y después `seed_data`.

---

## ¿Cómo ejecuto una sentencia SQL?

Hay tres caminos. Ordenados de más seguro a más riesgoso.

### Opción 1 — El ORM de Django (recomendado)

```bat
python manage.py shell
```

```python
from apps.config.models import SystemConfig
from apps.menu.models import Hamburger

config = SystemConfig.get_config()
config.tarifa_km = 500
config.save()

Hamburger.objects.filter(nombre__startswith='NICOTE').delete()
```

Es el camino recomendado porque respeta las validaciones de los modelos, dispara
las señales de Django y maneja bien las relaciones en cascada.

### Opción 2 — SQL directo desde Django

```bat
python manage.py dbshell
```

Abre la consola de SQLite ya apuntando al archivo correcto. Desde ahí es SQL puro:

```sql
UPDATE config_systemconfig SET tarifa_km = 500 WHERE id = 1;
SELECT id, nombre, precio_base FROM menu_hamburger;
DELETE FROM menu_hamburger WHERE nombre LIKE 'NICOTE%';
.tables
.schema orders_order
.quit
```

Los nombres de tabla siguen el patrón `<app>_<modelo en minúscula>`:
`menu_hamburger`, `orders_order`, `inventory_ingredient`, etc.

### Opción 3 — Interfaz gráfica

**DB Browser for SQLite** (sqlitebrowser.org, gratis). Se abre el archivo
`db.sqlite3`, se navegan las tablas con clicks y hay una pestaña "Execute SQL".

Importante: en esta herramienta los cambios quedan pendientes hasta apretar
**"Write Changes"**. Si se cierra sin eso, no se guardó nada.

### Precauciones

1. **Hacer una copia antes.** Es un solo archivo, copiarlo alcanza:
   ```bat
   copy db.sqlite3 db.sqlite3.backup
   ```

2. **Frenar el servidor** (`Ctrl+C` en la ventana del `runserver`) antes de
   escribir. Si no, puede aparecer el error `database is locked`.

3. **El SQL directo saltea toda la lógica de negocio.** Si se inserta un pedido a
   mano, no se descuenta stock, no se calcula el total ni se registra el historial
   de estados. Para datos reales conviene siempre la Opción 1 o la interfaz de la
   aplicación.

4. **Nunca cambiar el esquema con SQL** (`ALTER TABLE`, `CREATE TABLE`). Django
   lleva su propia contabilidad en la tabla `django_migrations`; si se modifica la
   estructura por fuera, queda desincronizada y el próximo `migrate` falla. Los
   cambios de estructura van siempre por `makemigrations` + `migrate`.

---

## ¿Qué hay adentro?

22 migraciones aplicadas el 04/08/2026 a las 23:42.

| Tabla | Filas | Contenido |
|---|---|---|
| `inventory_ingredient` | 18 | Ingredientes con stock |
| `inventory_recipe` | 34 | Recetas — todas de tipo hamburguesa |
| `inventory_inventorymovement` | 21 | Entradas y salidas de stock |
| `menu_hamburger` | 9 | Hamburguesas |
| `menu_addon` | 7 | Adicionales |
| `menu_addon_productos` | 29 | Relación adicional ↔ hamburguesa |
| `orders_order` | 8 | Pedidos |
| `orders_orderitem` | 8 | Productos dentro de cada pedido |
| `orders_orderitemaddon` | 9 | Adicionales por producto |
| `orders_orderstatushistory` | 21 | Cambios de estado |
| `config_systemconfig` | 1 | Configuración del sistema |
| `auth_user` | 1 | El usuario `admin` |

Estado de los 8 pedidos: 6 entregados, 1 cancelado, 1 pendiente.

Las 34 recetas son **todas** `producto_tipo='hamburger'`. No existe ni una sola
receta de adicional, lo que confirma que quitar esa opción de la pestaña Recetas
no rompe nada.

---

## El stack completo

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.14 |
| Framework | Django 4.2.x (`Django>=4.2,<5.0`) |
| Base de datos | SQLite 3 embebida / PostgreSQL opcional |
| Driver PostgreSQL | `psycopg2-binary>=2.9` (instalado, sin usar) |
| Frontend | Templates de Django + JavaScript vanilla |
| CSS | Propio, `static/css/styles.css`, con variables CSS nativas |
| Build | Ninguno — sin npm, sin webpack, sin Node |
| Servidor | `runserver` de Django (solo desarrollo) |

Solo dos dependencias en `requirements.txt`. Sin Django REST Framework, sin
React, sin Bootstrap ni Tailwind. Todo renderizado del lado del servidor.

### Navegador

La aplicación funciona en **cualquier navegador moderno** (Chrome, Edge, Firefox).
No hay dependencia de ninguno en particular: el HTML se arma en el servidor y el
JavaScript es vanilla sin transpilar. Se accede por `http://localhost:8000/`.

---

## Problemas detectados en los datos

### 1. La tarifa de envío tiene un valor de prueba

`config_systemconfig.tarifa_km` = **5.005.555** pesos por kilómetro.

Por eso el pedido #6 quedó con $15.016.665 de envío (3 km × la tarifa) y un total
de $100.958.306.

### 2. Dos precios impedirían migrar a PostgreSQL

`PositiveIntegerField` de Django se traduce a `integer` en PostgreSQL, cuyo máximo
es 2.147.483.647. SQLite tiene tipado dinámico y los aceptó igual, pero estos dos
valores están muy por encima:

| Registro | Valor |
|---|---|
| Hamburguesa `NICOTEWObbqqqqq` | $1.239.869.732.567.895.697 |
| Adicional `asdasdadad` | $12.341.412.515.151 |

Son registros de prueba, así que borrarlos resuelve el problema. Conviene además
agregar un máximo en la validación del formulario.

### 3. El pedido #8 tiene retiro en local y distancia a la vez

`retiro_local = 1` y `distancia_km = 5` simultáneamente. Alguien marcó "retira en
local" y dejó los 5 km escritos en el campo.

El cálculo lo ignoró correctamente y cobró $0 de envío, así que no hubo
consecuencias. Pero es exactamente el caso que se busca evitar con la mejora de
ocultar el campo de distancia.

### 4. El ingrediente Jamón quedó trabado

Está en `activo = 0` y ahora tiene un movimiento de salida (0,1 kg del pedido #8).

Cuando se lo desactivó no tenía ningún movimiento — por eso el sistema lo permitió.
Ahora que sí los tiene, la función `toggle_ingredient()` va a impedir
**reactivarlo**. Es el BUG-3 del [plan de mejoras](plan-mejoras-pendientes.md), reproducido en los
datos reales.

### 5. Quedaron tablas del panel de administración

La base tiene `django_admin_log` y los 64 permisos de `auth_permission` porque las
migraciones se aplicaron el 04/08 **antes** de que se quitara
`django.contrib.admin` de `INSTALLED_APPS`.

Son inofensivas, pero implican que la base actual y una base creada desde cero hoy
**no tienen el mismo esquema**. Si alguien borra `db.sqlite3` y corre `migrate`,
esas tablas ya no se crean.

---

## Documentos relacionados

- [plan-mejoras-pendientes.md](plan-mejoras-pendientes.md) — bugs, decisiones y tandas de trabajo
- [backend.md](backend.md) — qué hace cada módulo
- [ideas/cierre-del-dia.md](ideas/cierre-del-dia.md) — propuesta del módulo de cierre diario
- [README.md](../README.md) — instrucciones de instalación
