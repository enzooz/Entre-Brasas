# BASE DE DATOS — ENTRE BRASAS

## ¿Qué motor usamos?

**SQLite 3.** Es una base de datos que vive en **un solo archivo**. No hay un
servidor de base de datos corriendo aparte: SQLite es una librería que va
embebida dentro del proceso de Django. No hay nada que "prender", ni puerto que
escuchar, ni usuario y contraseña de base.

Es el único motor del proyecto: no se usa PostgreSQL ni ningún otro.

---

## ¿Dónde está el archivo?

| Dónde | Archivo |
|---|---|
| En desarrollo | `app/db.sqlite3` |
| En la compu del local | `%LOCALAPPDATA%\EntreBrasas\db.sqlite3` |

**No está versionada en git.** El `.gitignore` incluye `*.sqlite3`, así que los
datos son locales de cada máquina. Si otra persona clona el repo, arranca con la
base vacía y tiene que correr `migrate` y `seed_data`.

---

## Comandos

La base no se corre por separado: se levanta junto con Django. Estos comandos se
ejecutan desde `app`, con `.\venv\Scripts\python.exe manage.py <comando>`:

| Comando | Qué hace |
|---|---|
| `migrate` | Aplica las migraciones pendientes |
| `showmigrations` | Muestra cuáles están aplicadas |
| `makemigrations` | Genera una migración nueva tras cambiar un modelo |
| `shell` | Abre una consola Python con los modelos disponibles |
| `seed_data` | Carga el menú, los ingredientes y las recetas iniciales |
| `respaldar` | Guarda una copia de la base en `app/copias_de_seguridad/` |

Para empezar de cero: borrar `db.sqlite3`, correr `migrate` y después `seed_data`.

---

## ¿Cómo consulto o cambio datos?

### Opción 1: el ORM de Django (recomendado)

```python
from config.models import Configuracion
from menu.models import Hamburguesa

config = Configuracion.get_config()
config.tarifa_100m = 50
config.save()

Hamburguesa.objects.filter(nombre='Crispy').update(precio=14000)
```

Se escribe en la consola que abre `shell`. Es el camino recomendado porque maneja
bien las relaciones entre tablas.

### Opción 2: SQL directo

Con **DB Browser for SQLite** (sqlitebrowser.org, gratis): se abre el archivo
`db.sqlite3` y en la pestaña "Execute SQL" se escribe SQL común:

```sql
SELECT id, nombre, precio FROM menu_hamburguesa;
UPDATE config_configuracion SET tarifa_100m = 50 WHERE id = 1;
```

En esta herramienta los cambios quedan pendientes hasta apretar **"Write
Changes"**. Si se cierra sin eso, no se guardó nada.

El comando `dbshell` de Django hace lo mismo desde la consola, pero necesita
tener instalado el programa `sqlite3`.

### Precauciones

1. **Hacer una copia antes**, con el comando `respaldar`.
2. **Frenar el servidor** antes de escribir. Si no, puede aparecer el error
   `database is locked`.
3. **El SQL directo saltea la lógica del sistema.** Si se inserta un pedido a
   mano, no se descuenta stock, no se calcula el total ni se registra el
   historial de estados. Para datos reales conviene usar la aplicación.
4. **Nunca cambiar la estructura con SQL** (`ALTER TABLE`, `CREATE TABLE`). Django
   lleva su propia cuenta en la tabla `django_migrations`; si la estructura se
   modifica por fuera, el próximo `migrate` falla. Los cambios de estructura van
   siempre por `makemigrations` y `migrate`.

---

## Tablas

Los nombres siguen el patrón `<app>_<modelo en minúscula>`.

| Tabla | Qué guarda |
|---|---|
| `menu_hamburguesa` | Las hamburguesas del menú |
| `menu_adicional` | Los adicionales |
| `menu_adicional_hamburguesas` | Qué adicional se ofrece en qué hamburguesa |
| `inventario_ingrediente` | Los ingredientes y su stock |
| `inventario_receta` | Qué lleva cada hamburguesa o adicional |
| `inventario_movimientoinventario` | Entradas, salidas y conteos de stock |
| `pedidos_cliente` | Los clientes guardados |
| `pedidos_pedido` | Los pedidos |
| `pedidos_itempedido` | Las hamburguesas de cada pedido |
| `pedidos_adicionaldeitem` | Los adicionales de cada hamburguesa pedida |
| `pedidos_historialestado` | Los cambios de estado de cada pedido |
| `config_configuracion` | Tarifas, WhatsApp de cocina y datos del mapa |
| `django_migrations`, `django_content_type`, `django_session` | Internas de Django |

---

## Documentos relacionados

- [plan-mejoras-pendientes.md](plan-mejoras-pendientes.md): bugs, decisiones y tandas de trabajo
- [ideas/cierre-del-dia.md](ideas/cierre-del-dia.md): propuesta del módulo de cierre diario
- [README.md](../README.md): instrucciones de instalación
