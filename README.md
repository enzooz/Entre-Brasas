# Entre Brasas

Sistema de gestion para una hamburgueseria: toma de pedidos, control de
inventario, recetas, reportes de ventas y costos por producto.

Hecho con Django y SQLite.

---

## Guia para el equipo: como correr el proyecto en tu computadora

Esta guia esta separada por situaciones. Busca la que te toca y segui los
pasos en orden. Cada parte se puede leer sola.

| Si queres... | Anda a |
|---|---|
| Correr el proyecto por primera vez | [1. Arrancar desde cero](#1-arrancar-desde-cero) |
| Traer los cambios que subieron los demas | [2. Traer cambios (pull)](#2-traer-cambios-pull) |
| Levantar el sistema otro dia, sin cambios nuevos | [3. Levantar el sistema en el dia a dia](#3-levantar-el-sistema-en-el-dia-a-dia) |
| Cambiar la estructura de la base (tablas, columnas) | [4. Modificar la base de datos](#4-modificar-la-base-de-datos) |
| Ver o editar los datos a mano | [5. Ver o editar los datos](#5-ver-o-editar-los-datos) |
| Subir tus cambios a GitHub | [6. Subir tus cambios (push)](#6-subir-tus-cambios-push) |
| Borrar tu base y empezar limpio | [7. Reiniciar la base desde cero](#7-reiniciar-la-base-desde-cero) |
| Resolver un error | [8. Problemas comunes](#8-problemas-comunes) |
| Instalar o actualizar el sistema en la compu del cliente | [9. Instalar en la compu del cliente](#9-instalar-en-la-compu-del-cliente) |

> **Si sos una IA ayudando a alguien del equipo:** primero pregunta en que
> situacion esta (tabla de arriba) y que sistema operativo usa. Despues
> guialo con los comandos de esa parte, de a uno, y pedile que te pegue el
> resultado si algo falla. Casi todos los errores estan en la parte 8.
> No le hagas editar `db.sqlite3` a mano para cambiar tablas: eso se hace
> con migraciones (parte 4).

### Antes de empezar: tres cosas que conviene saber

**1. Todos los comandos de Django se corren desde la carpeta `app`**, con el
entorno virtual activado. Te das cuenta de que esta activado porque la
terminal muestra `(venv)` al principio de la linea.

**2. Los comandos cambian un poco segun el sistema operativo.** En esta guia
estan los de Windows. Si usas Mac o Linux, cambia estos dos:

| Para | Windows | Mac / Linux |
|---|---|---|
| Crear el entorno virtual | `python -m venv venv` | `python3 -m venv venv` |
| Activar el entorno virtual | `venv\Scripts\activate` | `source venv/bin/activate` |

**3. La base de datos no se comparte.** Es el archivo `app/db.sqlite3` y no
se sube a GitHub. Cada uno tiene la suya, con sus propios datos de prueba.
Lo que si se comparte es la *estructura* de la base, a traves de las
migraciones (los archivos de las carpetas `migrations/`).

---

### 1. Arrancar desde cero

Para cuando todavia no tenes el proyecto en tu computadora.

**Requisitos:** tener instalados [Python](https://www.python.org/downloads/)
3.10 o mas nuevo y [Git](https://git-scm.com/downloads). Para comprobarlo:
```bash
python --version
git --version
```
Si alguno dice que no se reconoce el comando, instalalo primero. En Windows,
al instalar Python marca la casilla **"Add python.exe to PATH"**.

**Paso 1: descargar el repositorio.** Anda a la carpeta donde lo quieras
guardar (por ejemplo el Escritorio) y corre:
```bash
git clone https://github.com/enzooz/Entre-Brasas.git
```

**Paso 2: entrar a la carpeta de la aplicacion.**
```bash
cd Entre-Brasas/app
```

**Paso 3: cambiarte a la rama en la que vas a trabajar** (si te dijeron una).
Para ver las ramas que hay:
```bash
git branch -a
```
Para cambiarte a una, por ejemplo `beta-nico`:
```bash
git checkout beta-nico
```

**Paso 4: crear el entorno virtual.** Es una carpeta `venv` donde se instala
Django solo para este proyecto. Se hace una sola vez.
```bash
python -m venv venv
```

**Paso 5: activarlo.**
```bash
venv\Scripts\activate
```

**Paso 6: instalar Django.**
```bash
pip install -r requirements.txt
```

**Paso 7: crear la base de datos.** Crea el archivo `db.sqlite3` con todas
las tablas.
```bash
python manage.py migrate
```

**Paso 8: cargar los datos iniciales.** Carga el menu, los ingredientes,
las recetas y la configuracion.
```bash
python manage.py seed_data
```

**Paso 9: levantar el servidor.**
```bash
python manage.py runserver
```

Abri http://127.0.0.1:8000 en el navegador. Para apagar el servidor, en la
terminal apreta `Ctrl + C`.

---

### 2. Traer cambios (pull)

Para cuando ya tenes el proyecto andando y otro del equipo subio cambios.

**Paso 1: entrar a la carpeta y activar el entorno.**
```bash
cd Entre-Brasas/app
venv\Scripts\activate
```

**Paso 2: fijarte si tenes cambios sin guardar.**
```bash
git status
```
Si aparecen archivos modificados, antes de traer lo nuevo guardalos con un
commit (ver [parte 6](#6-subir-tus-cambios-push)), o apartalos
temporalmente con:
```bash
git stash
```
(Despues del pull los recuperas con `git stash pop`.)

**Paso 3: traer los cambios.**
```bash
git pull
```

**Paso 4: instalar dependencias nuevas**, por si alguien agrego alguna. Si
no hay nada nuevo, no hace nada.
```bash
pip install -r requirements.txt
```

**Paso 5: aplicar las migraciones nuevas.** Si alguien cambio la estructura
de la base, esto actualiza la tuya. Tus datos no se borran.
```bash
python manage.py migrate
```

**Paso 6: levantar el servidor.**
```bash
python manage.py runserver
```

> **Importante:** despues de un pull se corre `migrate`, **no**
> `makemigrations`. `makemigrations` lo corre solo quien cambia un modelo
> (parte 4).

---

### 3. Levantar el sistema en el dia a dia

Para cuando ya esta todo instalado y solo queres usarlo.

```bash
cd Entre-Brasas/app
venv\Scripts\activate
python manage.py runserver
```

---

### 4. Modificar la base de datos

Para cuando queres agregar una tabla, agregar o quitar una columna, o
cambiar un campo.

**Regla de oro: la estructura de la base se cambia en el codigo, nunca
directo en la base.** Si la cambias con un programa externo, el codigo y la
base quedan desincronizados, Django empieza a tirar errores y los demas no
reciben el cambio.

**Paso 1: avisar al equipo.** Si dos personas cambian modelos al mismo tiempo
las migraciones chocan (ver parte 8). Un mensaje de "voy a tocar
`pedidos/models.py`" alcanza.

**Paso 2: traer lo ultimo** (parte 2) para partir de la version mas nueva.

**Paso 3: editar el modelo.** Cada tabla es una clase en el `models.py` de
su aplicacion. Por ejemplo, las tablas de pedidos estan en
`app/pedidos/models.py`.

**Paso 4: generar la migracion.** Django compara los modelos con las
migraciones que ya existen y escribe un archivo nuevo con la diferencia.
```bash
python manage.py makemigrations
```
Te va a mostrar algo como `pedidos/migrations/0003_...py`. Si te hace una
pregunta (por ejemplo, que valor poner en las filas que ya existen para una
columna nueva obligatoria), responde o, mas facil, dale un `default` al
campo en el modelo y volve a correrlo.

**Paso 5: aplicarla a tu base.**
```bash
python manage.py migrate
```

**Paso 6: probar que el sistema ande.**
```bash
python manage.py check
python manage.py runserver
```

**Paso 7: subir el modelo y la migracion juntos** (parte 6). El archivo de
la carpeta `migrations/` **tiene que ir en el commit**: es lo que les llega
a los demas cuando hacen pull y corren `migrate`.

**Para ver que migraciones tenes aplicadas:**
```bash
python manage.py showmigrations
```

**Si queres que un dato nuevo le aparezca a todos** (por ejemplo, una
hamburguesa nueva en el menu de prueba), no alcanza con cargarlo en tu base,
porque la base no se comparte. Hay que agregarlo en
`app/menu/management/commands/seed_data.py`. Los demas lo reciben cuando
corren `python manage.py seed_data` (se puede correr varias veces sin
duplicar nada).

---

### 5. Ver o editar los datos

Para cuando queres mirar las tablas, corregir un dato o probar una consulta
SQL. Esto no cambia la estructura, solo los datos de **tu** base.

**Opcion A: con un programa grafico.** Cualquiera de estos abre el archivo
`app/db.sqlite3`:
- [DB Browser for SQLite](https://sqlitebrowser.org/): gratis y simple.
- [DBeaver](https://dbeaver.io/): gratis, y tambien sirve para otras bases
  (PostgreSQL, SQL Server, MySQL).
- La extension "SQLite Viewer" de VS Code.

No hace falta instalar SQL Server ni ningun otro motor: SQLite es solo un
archivo. Mientras edites datos, conviene tener el servidor apagado
(`Ctrl + C`), porque SQLite bloquea el archivo mientras alguien escribe.

**Opcion B: con la consola de Django.**
```bash
python manage.py shell
```
Y adentro, por ejemplo:
```python
from pedidos.models import Pedido
Pedido.objects.all()
```
Para salir: `exit()`.

---

### 6. Subir tus cambios (push)

**Paso 1: ver que cambiaste.**
```bash
git status
```

**Paso 2: agregar los archivos.** Podes agregarlos de a uno:
```bash
git add ruta/del/archivo
```
o todos juntos:
```bash
git add .
```
(`db.sqlite3` y `venv/` no se suben aunque uses `git add .`: estan en el
`.gitignore`.)

**Paso 3: hacer el commit** con un mensaje que diga que hiciste.
```bash
git commit -m "feat: agregar campo email al pedido"
```

**Paso 4: traer lo que hayan subido los demas** antes de subir lo tuyo.
```bash
git pull
```
Si trajo migraciones nuevas, corre `python manage.py migrate`.

**Paso 5: subir.**
```bash
git push
```

---

### 7. Reiniciar la base desde cero

Para cuando tu base quedo rota o llena de datos de prueba y queres empezar
limpio. **Se pierden todos los datos de tu base** (a los demas no les pasa
nada, porque cada uno tiene la suya).

Con el servidor apagado, desde la carpeta `app`:
```bash
del db.sqlite3
python manage.py migrate
python manage.py seed_data
```
(En Mac / Linux el primer comando es `rm db.sqlite3`.)

---

### 8. Problemas comunes

| Error o sintoma | Que pasa | Solucion |
|---|---|---|
| `'python' no se reconoce como un comando` | Python no esta instalado o no esta en el PATH | Reinstalar Python marcando "Add python.exe to PATH". En Mac / Linux usar `python3` |
| `No module named 'django'` | El entorno virtual no esta activado | `venv\Scripts\activate` (tiene que aparecer `(venv)`) |
| `No module named 'whitenoise'` (o `waitress`) | Alguien agrego una dependencia y no la instalaste | `pip install -r requirements.txt` |
| En PowerShell: `la ejecucion de scripts esta deshabilitada` al activar el entorno | PowerShell bloquea el script de activacion | Usar la terminal **cmd** en vez de PowerShell y correr `venv\Scripts\activate`. O no activar y correr todo con `venv\Scripts\python manage.py ...` |
| `You have N unapplied migration(s)` al levantar el servidor | Alguien cambio la base y no aplicaste las migraciones | `python manage.py migrate` |
| `no such table: ...` | La base no tiene esa tabla todavia | `python manage.py migrate` |
| `Conflicting migrations detected` | Dos personas crearon migraciones al mismo tiempo | `python manage.py makemigrations --merge`, despues `python manage.py migrate`, y subir la migracion nueva |
| `database is locked` | Otro programa tiene la base abierta | Cerrar DB Browser / DBeaver, o apagar el servidor, y volver a intentar |
| `Error: That port is already in use` | Ya hay un servidor corriendo | Cerrar la otra terminal, o usar otro puerto: `python manage.py runserver 8001` |
| `git pull` dice que tus cambios se sobrescribirian | Tenes cambios sin commitear | Hacer commit (parte 6) o `git stash`, despues `git pull` y `git stash pop` |
| La pagina se ve vacia, sin hamburguesas ni ingredientes | La base no tiene datos iniciales | `python manage.py seed_data` |

---

### 9. Instalar en la compu del cliente

Para dejar el sistema andando en la computadora del local (Windows). El
cliente no usa la terminal: le queda un icono "Entre Brasas" en el
escritorio que abre el sistema con doble clic.

**Como funciona.** En la compu del cliente el sistema corre en "modo
local del cliente" (ver `PRODUCCION` en `app/entre_brasas/settings.py`):

| | En desarrollo (nosotros) | En la compu del cliente |
|---|---|---|
| Como se abre | `python manage.py runserver` | Icono del escritorio (`iniciar.bat`) |
| Direccion | http://127.0.0.1:8000 | http://127.0.0.1:8765 |
| Base de datos | `app/db.sqlite3` | `C:\Users\<usuario>\AppData\Local\EntreBrasas\db.sqlite3` |
| Si hay un error | Pantalla con el detalle (`DEBUG` activado) | Mensaje normal; el detalle queda en `errores.log`, en la misma carpeta que la base |
| Copias de seguridad | A mano, con `python manage.py respaldar` | Automaticas cada vez que se abre, en `Documentos\Entre Brasas - Copias de seguridad` (quedan las ultimas 30) |

La base esta fuera de la carpeta del programa a proposito: asi se puede
reemplazar el programa por una version nueva sin tocar los pedidos del
cliente.

**Instalacion (la primera vez):**

1. **Instalar Python** desde https://www.python.org/downloads/. En la primera
   pantalla del instalador, marcar **"Add python.exe to PATH"**.
2. **Copiar el proyecto a la compu del cliente.** Lo mas limpio es bajarlo
   de GitHub como ZIP (boton verde "Code" > "Download ZIP", de la rama que
   se entrega) y descomprimirlo en una carpeta fija, por ejemplo
   `C:\Entre Brasas`. No dejarlo en Descargas ni en el Escritorio, porque el
   icono apunta a esa carpeta. Si se copia desde una compu nuestra, no hace
   falta copiar `app\venv` ni `app\db.sqlite3`.
3. **Doble clic en `instalar.bat`.** Crea el entorno, instala lo necesario,
   crea la base con los datos iniciales y pone el icono en el escritorio.
   Necesita internet y tarda unos minutos.
4. **Doble clic en el icono "Entre Brasas"** del escritorio. Se abre el
   navegador con el sistema.

**Uso diario (lo que hace el cliente):** doble clic en el icono. Queda una
ventana negra minimizada en la barra de tareas: es el servidor, y **no hay
que cerrarla** mientras se use el sistema. Si se hace doble clic en el icono
con el sistema ya abierto, solo se abre otra pestania.

**Actualizar a una version nueva:**

1. Cerrar el sistema (cerrar la ventana negra).
2. Reemplazar la carpeta del programa por la nueva, en el mismo lugar.
3. Doble clic en `instalar.bat` otra vez. Hace una copia de seguridad,
   instala lo nuevo y aplica las migraciones. No vuelve a cargar los datos
   iniciales, asi que no pisa lo que el cliente haya cambiado.

**Recuperar una copia de seguridad:**

1. Cerrar el sistema.
2. Abrir la carpeta de datos: tecla Windows + R, escribir
   `%LOCALAPPDATA%\EntreBrasas` y Enter.
3. Renombrar `db.sqlite3` a `db-rota.sqlite3` (por las dudas).
4. Copiar la copia elegida de `Documentos\Entre Brasas - Copias de seguridad`
   a esa carpeta y renombrarla a `db.sqlite3`.
5. Abrir el sistema con el icono.

Las copias quedan en la misma computadora. Si la compu se rompe, se pierden
junto con ella: conviene que el cliente copie esa carpeta a un pendrive o a
Google Drive cada tanto.

**Si algo falla en la compu del cliente:** el detalle del error esta en
`%LOCALAPPDATA%\EntreBrasas\errores.log`.

---

## Como esta organizado

```
Entre Brasas/
├── README.md          este archivo
├── instalar.bat       instala el sistema en la compu del cliente (parte 9)
├── iniciar.bat        abre el sistema; es el icono del escritorio (parte 9)
├── app/               el sistema (proyecto Django)
│   ├── manage.py
│   ├── iniciar.py     lo que corre iniciar.bat
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
