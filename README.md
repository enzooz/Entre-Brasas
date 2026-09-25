# Entre Brasas

Sistema de gestion para una hamburgueseria: toma de pedidos, control de
inventario, recetas, reportes de ventas y costos por producto.

Hecho con Django y SQLite.

---

## Como levantar el sistema

### 1. Requisitos
Python 3.10 o mas nuevo.

### 2. Ir a la carpeta de la aplicacion
```bash
cd app
```

### 3. Crear el entorno virtual
```bash
python -m venv venv
```

### 4. Activarlo
```bash
venv\Scripts\activate
```

### 5. Instalar Django
```bash
pip install -r requirements.txt
```

### 6. Crear la base de datos
```bash
python manage.py migrate
```

### 7. Cargar los datos iniciales
Carga el menu, los ingredientes, las recetas y la configuracion.
```bash
python manage.py seed_data
```

### 8. Levantar el servidor
```bash
python manage.py runserver
```

Despues entrar a http://127.0.0.1:8000

---

## Como esta organizado

```
Entre Brasas/
├── README.md          este archivo
├── app/               el sistema (proyecto Django)
│   ├── manage.py
│   ├── requirements.txt
│   ├── entre_brasas/  configuracion general
│   ├── pedidos/ menu/ inventario/ reportes/ costos/ config/
│   ├── templates/
│   └── static/
└── docs/              documentacion del proyecto
```

### Documentacion

| Documento | De que trata |
|---|---|
| [docs/backend.md](docs/backend.md) | Que hace cada modulo del backend |
| [docs/base-de-datos.md](docs/base-de-datos.md) | Motor, esquema, datos y como se corre la base |
| [docs/plan-mejoras-pendientes.md](docs/plan-mejoras-pendientes.md) | Bugs, decisiones y tandas de trabajo pendientes |
| [docs/ideas/cierre-del-dia.md](docs/ideas/cierre-del-dia.md) | Propuesta del modulo "Cerrar el dia" |
| [docs/presentacion-alcance-completo.pdf](docs/presentacion-alcance-completo.pdf) | Presentacion del alcance del proyecto |

### Dentro de `app/`

El sistema esta dividido en seis aplicaciones, una por cada parte del negocio:

| Carpeta | De que se ocupa |
|---|---|
| `pedidos/` | Tomar pedidos, avanzarlos de estado y cancelarlos |
| `menu/` | Hamburguesas y adicionales |
| `inventario/` | Ingredientes, stock, movimientos y recetas |
| `reportes/` | Reportes de ventas |
| `costos/` | Cuanto cuesta y cuanto deja cada hamburguesa |
| `config/` | Tarifas de envio y costo de mano de obra |

Ademas hay tres carpetas que no son aplicaciones:

| Carpeta | Que tiene |
|---|---|
| `entre_brasas/` | La configuracion general del proyecto |
| `templates/` | Las pantallas HTML |
| `static/` | El archivo de estilos |

#### Dentro de cada aplicacion

Los archivos siempre se llaman igual y hacen siempre lo mismo:

| Archivo | Que hace |
|---|---|
| `models.py` | Define las tablas de la base de datos |
| `views.py` | Atiende cada pantalla: recibe el pedido del navegador y responde |
| `forms.py` | Arma y valida los formularios |
| `urls.py` | Dice que direccion corresponde a cada pantalla |

La aplicacion `pedidos` tiene ademas un archivo `calculos.py`, donde estan
las cuentas del sistema (costo de envio, total del pedido y descuento de
stock). La idea es que `views.py` se ocupe de las pantallas y `calculos.py`
de las cuentas.

---

## Como funciona un pedido

1. Se carga el pedido y queda en estado **pendiente**.
2. Cuando la cocina lo empieza, pasa a **en preparacion** y ahi el sistema
   descuenta del inventario los ingredientes segun la receta.
3. Cuando sale para entregar, pasa a **en camino**.
4. Cuando llega, pasa a **entregado** y recien ahi cuenta como venta en los
   reportes.

Un pedido se puede cancelar en cualquier momento antes de entregarlo. Si ya
habia descontado stock, se puede elegir devolver los ingredientes al
inventario o registrarlos como perdida.

---

## Decisiones que tomamos

**No tiene usuarios ni contrasenia.** El sistema lo usa una sola persona,
desde la computadora del local. Agregar un login no aportaba nada al caso
de uso real.

**Los precios se guardan como numeros enteros de pesos.** No usamos centavos
porque los precios del rubro son redondos.

**El precio se copia al pedido.** Cuando se carga un pedido, se guarda una
copia del precio de ese momento. Asi, si manana sube el precio de una
hamburguesa, los pedidos viejos siguen mostrando lo que el cliente pago.

**Nada se borra, se desactiva.** Las hamburguesas, los adicionales y los
ingredientes tienen un campo para darlos de baja. Si se borraran, los
pedidos historicos que los incluyen quedarian rotos.

**Los movimientos de stock no se editan.** Para revertir algo se crea el
movimiento contrario. Asi queda el historial completo de lo que paso.
