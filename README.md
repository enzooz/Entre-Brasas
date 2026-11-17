# Entre Brasas

Sistema de gestion para una hamburgueseria: toma de pedidos, control de
inventario, recetas, reportes de ventas y costos por producto.

Hecho con Django y SQLite.

Mapa integrado, clave Geoapify y tarifa editable por 100 metros:
[guía de mapa y envíos](docs/mapa-y-envios.md).

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

**1. Todos los comandos de Django se corren desde la carpeta `app`.** Esta
guia usa PowerShell y llama directamente al Python del entorno
con `.\venv\Scripts\python.exe`. No hace falta activar el entorno ni cambiar
los permisos de ejecucion de PowerShell.

**2. Los comandos cambian un poco segun el sistema operativo.** En esta guia
estan los de Windows. Si usas Mac o Linux, usa estos equivalentes:

| Para | Windows | Mac / Linux |
|---|---|---|
| Crear el entorno virtual | `py -3.12 -m venv venv` | `python3.12 -m venv venv` |
| Ejecutar Python del entorno | `.\venv\Scripts\python.exe` | `./venv/bin/python` |

La aplicacion web se puede desarrollar en esos sistemas; el instalador,
el acceso directo y el arranque con `iniciar.py` son especificos de Windows.

**3. La base de datos no se comparte.** Es el archivo `app/db.sqlite3` y no
se sube a GitHub. Cada uno tiene la suya, con sus propios datos de prueba.
Lo que si se comparte es la *estructura* de la base, a traves de las
migraciones (los archivos de las carpetas `migrations/`).

---

### 1. Arrancar desde cero

Para cuando todavia no tenes el proyecto en tu computadora.

**Requisitos:** tener instalados [Python](https://www.python.org/downloads/)
**3.12** y [Git](https://git-scm.com/downloads). Es la version de Python con
la que se verifico la suite del proyecto; no asumir que una mas nueva es
compatible con todas las pruebas. Para comprobarlo:
```powershell
py -3.12 --version
git --version
```
Si alguno dice que no se reconoce el comando, instalalo primero. En Windows,
al instalar Python marca la casilla **"Add python.exe to PATH"**.

Para clonar un repositorio privado y subir tu rama, tu cuenta de GitHub debe
tener el acceso correspondiente al repo. Si no lo tenes, pediselo al equipo.

**Paso 1: descargar el repositorio.** Anda a la carpeta donde lo quieras
guardar (por ejemplo el Escritorio) y corre:
```powershell
git clone --branch master https://github.com/enzooz/Entre-Brasas.git
```

**Paso 2: entrar a la carpeta de la aplicacion.**
```powershell
cd Entre-Brasas/app
```

**Paso 3: crear tu rama de trabajo desde master.** Cada desarrollador trabaja
en su propia rama y propone los cambios mediante un Pull Request hacia
`master`; no subas modificaciones directamente a `master`.
```powershell
git switch -c codex/mi-mejora
```
Reemplaza `mi-mejora` por un nombre que describa tu cambio. Si el equipo ya
te asigno una rama, usa `git switch nombre-de-la-rama` en vez de crear otra.

**Paso 4: crear el entorno virtual.** Es una carpeta `venv` donde se instala
Django solo para este proyecto. Se hace una sola vez.
```powershell
py -3.12 -m venv venv
```

**Paso 5: comprobar el Python del entorno.** No hace falta activarlo.
```powershell
.\venv\Scripts\python.exe --version
```

**Paso 6: instalar las dependencias del proyecto.**
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Paso 7: crear la base de datos.** Crea el archivo `db.sqlite3` con todas
las tablas.
```powershell
.\venv\Scripts\python.exe manage.py migrate
```

**Paso 8: cargar los datos iniciales.** Carga el menu, los ingredientes,
las recetas y la configuracion, solo si la base todavia esta vacia. El stock
inicial queda en 0; no trae pedidos ni datos de la PC del cliente.
```powershell
.\venv\Scripts\python.exe manage.py seed_data --si-esta-vacia
```

**Paso 9: levantar el servidor.**
```powershell
.\venv\Scripts\python.exe manage.py runserver
```

Abri http://127.0.0.1:8000 en el navegador. Para apagar el servidor, en la
terminal apreta `Ctrl + C`.

Para desarrollar no uses `instalar.bat` ni el icono del cliente: esos usan
otra base en AppData y no el servidor de desarrollo (ver parte 9).

---

### 2. Traer cambios (pull)

Para cuando ya tenes el proyecto andando y otro del equipo subio cambios.

**Paso 1: entrar a la carpeta y detener runserver si esta abierto.**
```powershell
cd Entre-Brasas/app
```

**Paso 2: fijarte si tenes cambios sin guardar.**
```powershell
git status
```
Si aparecen archivos modificados, antes de traer lo nuevo guardalos con un
commit (ver [parte 6](#6-subir-tus-cambios-push)), o apartalos
temporalmente con:
```powershell
git stash push -u -m "Trabajo antes de actualizar"
```
(Despues del pull los recuperas con `git stash pop`.)

**Paso 3: traer los cambios de tu rama.** Si ya tiene una rama remota:
```powershell
git pull --ff-only
```
Esto actualiza la rama actual, no cambia automaticamente a `master`. Si tu
rama es nueva y todavia no tiene rama remota, omiti ese pull. Para incorporar
los cambios del equipo en `master` a tu rama de trabajo:
```powershell
git fetch origin
git merge origin/master
```
Si aparecen conflictos, resolvelos y revisa el resultado antes de seguir.
Si `pull --ff-only` indica que las ramas divergieron, no fuerces el push:
coordina la integracion con el equipo. Para actualizar solo tu copia de
`master`, con el trabajo guardado: `git switch master` y `git pull --ff-only`.

**Paso 4: instalar dependencias nuevas**, por si alguien agrego alguna. Si
no hay nada nuevo, no hace nada.
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Paso 5: aplicar las migraciones nuevas.** Si alguien cambio la estructura
de la base, esto actualiza la tuya. Tus datos no se borran.
```powershell
.\venv\Scripts\python.exe manage.py migrate
```

**Paso 6: levantar el servidor.**
```powershell
.\venv\Scripts\python.exe manage.py runserver
```

> **Importante:** despues de un pull se corre `migrate`, **no**
> `makemigrations`. `makemigrations` lo corre solo quien cambia un modelo
> (parte 4).

---

### 3. Levantar el sistema en el dia a dia

Para cuando ya esta todo instalado y solo queres usarlo.

```powershell
cd Entre-Brasas/app
.\venv\Scripts\python.exe manage.py runserver
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
```powershell
.\venv\Scripts\python.exe manage.py makemigrations
```
Te va a mostrar algo como `pedidos/migrations/0003_...py`. Si te hace una
pregunta (por ejemplo, que valor poner en las filas que ya existen para una
columna nueva obligatoria), responde o, mas facil, dale un `default` al
campo en el modelo y volve a correrlo.

**Paso 5: aplicarla a tu base.**
```powershell
.\venv\Scripts\python.exe manage.py migrate
```

**Paso 6: probar que el sistema ande.**
```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test
.\venv\Scripts\python.exe manage.py runserver
```

**Paso 7: subir el modelo y la migracion juntos** (parte 6). El archivo de
la carpeta `migrations/` **tiene que ir en el commit**: es lo que les llega
a los demas cuando hacen pull y corren `migrate`.

**Para ver que migraciones tenes aplicadas:**
```powershell
.\venv\Scripts\python.exe manage.py showmigrations
```

**Si queres que un dato nuevo le aparezca a todos** (por ejemplo, una
hamburguesa nueva en el menu de prueba), no alcanza con cargarlo en tu base,
porque la base no se comparte. Hay que agregarlo en
`app/menu/management/commands/seed_data.py`. Los demas lo reciben cuando
corren `.\venv\Scripts\python.exe manage.py seed_data` (se puede correr varias
veces sin duplicar nada; conserva registros existentes). Para actualizar
productos ya cargados, usa una migracion de datos o una opcion explicita
del comando, no edites la base del cliente.

**Si la base conserva el menú de prueba anterior (BBQ, Clásica, etc.):**
desde `app`, corré primero `.\venv\Scripts\python.exe manage.py respaldar`, después
`.\venv\Scripts\python.exe manage.py migrate` y finalmente
`.\venv\Scripts\python.exe manage.py seed_data --reemplazar-menu`. Esta opción carga el menú real,
actualiza sus precios y desactiva los productos anteriores sin borrar pedidos
ni modificar el stock existente. El comando normal conserva los datos ya
cargados; un `git pull` por sí solo no actualiza el menú de la base.

La configuración del envío ahora expresa la tarifa por **100 metros**. La
migración divide la tarifa anterior por 10 para conservar el precio equivalente.
La distancia se ingresa en kilómetros con hasta un decimal. El envío mínimo
cubre la **distancia incluida** configurada; después se suma la tarifa solo por
los metros excedentes: `mínimo + max(0, km - km incluidos) × 10 × tarifa por 100 m`.
Ejemplo: $1000 hasta 1 km y $100 cada 100 m adicionales → 0,1–1 km cuesta
$1000, 1,1 km cuesta $1100 y 1,3 km cuesta $1300. Retirar en el local cuesta $0.
Se conserva la configuración existente y no se recalculan pedidos históricos.

Nuevo pedido se carga en cuatro paneles: **Cliente → Hamburguesas → Pago →
Ubicación**. Atrás conserva los datos; Continuar valida el paso. El total y los
controles quedan fuera del panel desplazable para pedidos largos. Cliente crece
con sus campos y avisos sin scroll interno; en ventanas bajas o celular se puede
desplazar la página. Nombre y teléfono quedan alineados en escritorio y se apilan
en celular para conservar su legibilidad.
El borrador por pestaña guarda también el paso; solamente Crear pedido al final
envía los datos. Buscar un cliente o pegar WhatsApp sigue siendo opcional.

---

### 5. Ver o editar los datos

Para cuando queres mirar las tablas, corregir un dato o probar una consulta
SQL. Esto no cambia la estructura, solo los datos de **tu** base.

**Opcion A: con un programa grafico.** Cualquiera de estos abre el archivo
`app/db.sqlite3`:
- [DB Browser for SQLite](https://sqlitebrowser.org/): gratis y simple.
- [DBeaver](https://dbeaver.io/): gratis y mas completo.
- La extension "SQLite Viewer" de VS Code.

No hace falta instalar SQL Server ni ningun otro motor: SQLite es solo un
archivo. Mientras edites datos, conviene tener el servidor apagado
(`Ctrl + C`), para evitar escrituras simultaneas sobre tu base de prueba.

**Opcion B: con la consola de Django.**
```powershell
.\venv\Scripts\python.exe manage.py shell
```
Y adentro, por ejemplo:
```python
from pedidos.models import Pedido
Pedido.objects.all()
```
Para salir: `exit()`.

---

### 6. Subir tus cambios (push)

Trabaja en tu rama, no en `master`. Si todavia no creaste una, partiendo de
`master` actualizado ejecuta `git switch -c codex/mi-mejora` antes de editar.

**Paso 1: comprobar la rama y ver que cambiaste.**
```powershell
git branch --show-current
git status
git diff
```

**Paso 2: revisar el sistema y las migraciones**, desde `app`:
```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
```
Si cambiaste JavaScript, necesitas Node.js para ejecutar tambien estas pruebas
desde `app` (no se necesita para instalar o usar la aplicacion):
```powershell
node --test tests/javascript/*.cjs
```
Proba tambien el flujo que modificaste en el navegador. Las pruebas de
arranque del instalador solo se ejecutan en Windows.

**Paso 3: agregar los archivos del cambio.** Podes agregarlos de a uno:
```powershell
git add ruta/del/archivo
```
Si estas dentro de `app`, las rutas son relativas a esa carpeta. Para incluir
cambios de la raiz (por ejemplo README), usa su ruta, como `../README.md`.
Antes de commitear, revisa exactamente lo que vas a subir:
```powershell
git diff --cached
```
No subas bases, respaldos, entornos virtuales, claves ni datos del cliente.
`*.sqlite3` y `venv/` estan excluidos por `.gitignore`; igualmente revisa
la lista. Si modificaste modelos, inclui sus migraciones en el mismo commit.

**Paso 4: hacer el commit** con un mensaje que diga que hiciste.
```powershell
git commit -m "feat: agregar campo email al pedido"
```

**Paso 5: incorporar los cambios de master**, manteniendote en tu rama:
```powershell
git fetch origin
git merge origin/master
```
Si tu rama ya se comparte con otros, incorpora tambien sus cambios remotos
(ver parte 2). Resolve los conflictos si aparecen, instala las dependencias
y aplica las migraciones nuevas; despues repeti las pruebas.

**Paso 6: subir tu rama.** Usa el nombre que elegiste (este es un ejemplo):
```powershell
git push -u origin codex/mi-mejora
```
**Paso 7: abrir un Pull Request en GitHub**, con `master` como rama destino
(`base`) y tu rama como origen (`compare`). Explica el cambio y las pruebas
que hiciste. El equipo lo revisa y lo integra; no hagas push directo a
`master` ni uses push forzado.

---

### 7. Reiniciar la base desde cero

Para cuando tu base quedo rota o llena de datos de prueba y queres empezar
limpio. **Se pierden todos los datos de tu base** (a los demas no les pasa
nada, porque cada uno tiene la suya).

Con el servidor apagado, desde la carpeta `app`:
```powershell
Remove-Item -LiteralPath .\db.sqlite3
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_data --si-esta-vacia
```
(En Mac / Linux el primer comando es `rm db.sqlite3`.)

---

### 8. Problemas comunes

| Error o sintoma | Que pasa | Solucion |
|---|---|---|
| `'py' no se reconoce` o `No suitable Python runtime found` | Falta Python 3.12 o el lanzador de Python | Instalar Python 3.12 con el lanzador y "Add python.exe to PATH"; comprobar `py -3.12 --version`. En Mac / Linux usar `python3.12` |
| No se encuentra `.\venv\Scripts\python.exe` | No estas en `app` o no creaste el entorno | Entrar a `app` y ejecutar `py -3.12 -m venv venv` |
| `No module named 'django'`, `whitenoise` o `waitress` | Estas usando otro Python o faltan dependencias | Usar `.\venv\Scripts\python.exe` e instalar con `.\venv\Scripts\python.exe -m pip install -r requirements.txt` |
| En PowerShell: `la ejecucion de scripts esta deshabilitada` al activar el entorno | PowerShell bloquea el script de activacion | No activarlo: usar `.\venv\Scripts\python.exe manage.py ...`, como en esta guia |
| `You have N unapplied migration(s)` al levantar el servidor | Alguien cambio la base y no aplicaste las migraciones | `.\venv\Scripts\python.exe manage.py migrate` |
| `no such table: ...` | La base no tiene esa tabla todavia | `.\venv\Scripts\python.exe manage.py migrate` |
| `Conflicting migrations detected` | Dos personas crearon migraciones al mismo tiempo | Coordinar con quienes modificaron los modelos; revisar las operaciones y, si son compatibles, usar `.\venv\Scripts\python.exe manage.py makemigrations --merge`, aplicar y subir la migracion |
| `database is locked` | Otro programa tiene la base abierta | Cerrar DB Browser / DBeaver, o apagar el servidor, y volver a intentar |
| `Error: That port is already in use` | Ya hay un servidor corriendo | Detenerlo con `Ctrl + C`, o usar otro puerto: `.\venv\Scripts\python.exe manage.py runserver 8001` |
| `git pull` dice que tus cambios se sobrescribirian | Tenes cambios sin commitear | Guardarlos como en la parte 2 y usar `git pull --ff-only`; recuperar el stash y resolver conflictos si aparecen |
| `git pull --ff-only` indica que las ramas divergieron | Hay commits distintos en local y remoto | Coordinar la integracion con el equipo; no usar push forzado |
| La pagina se ve vacia, sin hamburguesas ni ingredientes | La base no tiene datos iniciales | `.\venv\Scripts\python.exe manage.py seed_data --si-esta-vacia` |

---

### 9. Instalar en la compu del cliente

Para dejar el sistema andando en la computadora del local (Windows). El
cliente no usa la terminal: le queda un icono "Entre Brasas" en el
escritorio que abre el sistema con doble clic.

**Como funciona.** En la compu del cliente el sistema corre en "modo
local del cliente" (ver `PRODUCCION` en `app/entre_brasas/settings.py`):

| | En desarrollo (nosotros) | En la compu del cliente |
|---|---|---|
| Como se abre | `.\venv\Scripts\python.exe manage.py runserver` | Icono del escritorio (`pythonw.exe iniciar.py`, sin consola) |
| Direccion | http://127.0.0.1:8000 | http://127.0.0.1:8765 |
| Base de datos | `app/db.sqlite3` | `C:\Users\<usuario>\AppData\Local\EntreBrasas\db.sqlite3` |
| Si hay un error | Pantalla con el detalle (`DEBUG` activado) | Mensaje normal; el detalle queda en `errores.log`, en la misma carpeta que la base |
| Copias de seguridad | A mano, con `.\venv\Scripts\python.exe manage.py respaldar` | Automaticas cada vez que se abre, en `Documentos\Entre Brasas - Copias de seguridad` (quedan las ultimas 30) |

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

**El stock arranca en 0, y no pasa nada.** El sistema nunca frena un pedido
por falta de stock: descuenta igual, el número puede quedar en negativo y
avisa. Así el local puede trabajar desde el primer día sin haber cargado el
inventario. Cuando cuenten lo que hay en la cocina, se carga desde
**Inventario → Registrar movimiento → Conteo**: se escribe la cantidad real
y el sistema ajusta el stock solo. Se puede hacer de a un ingrediente, cuando
tengan tiempo.

**Uso diario (lo que hace el cliente):** doble clic en el icono. El servidor
arranca en segundo plano, sin ventana negra. Cerrar el navegador no apaga
Entre Brasas; se puede volver a abrir desde el mismo icono.

**Para apagar:** dentro de la web, al pie del menú, tocar **Apagar sistema**
y después **Sí, apagar sistema**. Antes guardar los formularios abiertos:
se conservan los pedidos guardados, no los cambios que todavía no se enviaron.
Esto apaga Entre Brasas para todas las pestañas, no la computadora. Para
volver a trabajar, abrir otra vez el icono del escritorio. No hay un acceso
extra para apagar en el escritorio.

Las pantallas que ya estaban abiertas quedan en gris y bloqueadas, con el
aviso **Sistema apagado**. No se pueden editar campos, guardar ni usar las
acciones del menú. Las otras pestañas reciben el aviso y también se bloquean.
Si el servidor deja de responder sin un apagado confirmado, el aviso dice
**Sistema sin conexión** y se aplica el mismo bloqueo. Al reabrir desde el
icono, aparece **Volver al inicio**: carga los datos actuales sin enviar
automáticamente formularios pendientes.

**Pedido a medio cargar:** Nuevo pedido guarda un borrador automático en esa
pestaña del navegador. Se puede ir a otra sección, volver o recargar y seguir
con cliente, hamburguesas, extras por unidad, notas, envío, pago y mensaje de
WhatsApp. No crea un pedido ni envía esos datos al servidor. El borrador se
limpia después de crear correctamente el pedido, o con **Descartar borrador**
y su confirmación. Cada pestaña mantiene su propio borrador; cerrar la pestaña
termina esa sesión. Al recuperarlo se usan los precios y tarifas actuales y
se avisa si algún producto o extra ya no está disponible.

**Clientes guardados:** en Nuevo pedido, buscá por nombre o teléfono y elegí un
resultado para completar nombre, teléfono y dirección. Revisá la dirección y
volvé a ingresar la distancia si cambió. **Cliente nuevo** limpia esos datos, no
las hamburguesas. Los datos del cliente se guardan al crear correctamente el
pedido; un error no deja registros parciales. Se conserva una copia de los datos
en cada pedido, así actualizar el cliente no cambia ventas anteriores.

Los pedidos existentes con teléfono identificable se vinculan automáticamente
al aplicar las migraciones. Se agrupan por los dígitos del teléfono, sin inferir
país ni prefijos. Sin teléfono, no se unen personas por su nombre: para reutilizar
un cliente sin teléfono, elegilo en la búsqueda. Retiro sigue admitiendo solo nombre.

**Baja de ingredientes:** los movimientos anteriores no impiden desactivar un
insumo. Sí lo impide una receta de hamburguesa o adicional activo que lo use.
Primero quitá el insumo de esas recetas o desactivá los productos; el historial
y el stock no se borran.

**Prueba técnica de instalación (Windows):** desde la raíz, ejecutar
`app\venv\Scripts\python.exe app\entre_brasas\probar_instalacion.py`.
Necesita internet y usa una copia aislada: no toca tu base ni tu escritorio.
Comprueba instalación, stock inicial 0, acceso sin consola y actualización sin
pisar datos. La prueba de arranque/apagado/reapertura está en la suite Django.

Si se hace doble clic con el sistema ya abierto, solo se abre otra pestaña.
Si hay un error de arranque, aparece un aviso y el detalle queda en
`servidor.log`, junto a la base del cliente. El instalador sigue mostrando
su progreso una sola vez; esa ventana se puede cerrar cuando dice Listo.

**Actualizar a una version nueva:**

1. Apagar el sistema desde el botón de la web y confirmar.
2. Reemplazar la carpeta del programa por la nueva, en el mismo lugar.
3. Doble clic en `instalar.bat` otra vez. Hace una copia de seguridad,
   instala lo nuevo y aplica las migraciones. No vuelve a cargar los datos
   iniciales, asi que no pisa lo que el cliente haya cambiado.

**Recuperar una copia de seguridad:**

1. Apagar el sistema desde la web y confirmar.
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
│   ├── tests/javascript/  pruebas del navegador ejecutadas con Node.js
│   └── static/
└── docs/              documentacion del proyecto
```

### Documentacion

Empezá por el [índice de documentación](docs/README.md). Para la defensa,
consultá la [guía de estructura y recorrido del código](docs/estructura-y-defensa.md).

| Documento | De que trata |
|---|---|
| [docs/base-de-datos.md](docs/base-de-datos.md) | Motor, tablas y como consultar la base |
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
| `config/` | Tarifas de envio, mano de obra, WhatsApp y mapas |

Ademas hay carpetas de infraestructura, presentación y pruebas:

| Carpeta | Que tiene |
|---|---|
| `entre_brasas/` | La configuracion general del proyecto |
| `templates/` | Las pantallas HTML |
| `static/` | CSS, JavaScript, fuentes, imágenes y Leaflet |
| `tests/javascript/` | Pruebas de la interacción del formulario y del estado del sistema |

#### Dentro de cada aplicacion

Los archivos siguen las convenciones de Django. Cada módulo contiene los que necesita
(por ejemplo, reportes y costos consultan modelos de otros módulos):

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
