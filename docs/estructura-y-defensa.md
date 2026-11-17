# Estructura del proyecto y guía para la defensa

Entre Brasas es una aplicación web local de gestión de una hamburguesería.
Está construida con Django y SQLite, con pantallas HTML y JavaScript. La
separación principal sigue las áreas del negocio; no son microservicios.

## Mapa de carpetas

```text
Entre Brasas/
├── README.md                 Instalación y desarrollo
├── instalar.bat              Instalación para Windows
├── iniciar.bat               Inicio del sistema instalado
├── PRODUCT.md / DESIGN.md    Objetivo y convenciones de interfaz
├── docs/                     Guías, presentación e ideas
└── app/
    ├── manage.py             Comandos de Django
    ├── iniciar.py            Servidor local y apertura de la aplicación
    ├── requirements.txt      Dependencias de Python
    ├── entre_brasas/         Configuración, rutas principales y estado del servidor
    ├── pedidos/              Clientes, pedidos, envío, comanda y mapas
    ├── menu/                 Hamburguesas y adicionales
    ├── inventario/           Ingredientes, recetas y movimientos de stock
    ├── reportes/             Consultas de ventas
    ├── costos/               Consultas de costos y ganancias
    ├── config/               Parámetros del negocio y respaldos
    ├── templates/            Pantallas HTML agrupadas por módulo
    ├── static/               CSS, JS, fuentes, imágenes y librerías externas
    └── tests/javascript/     Pruebas de interacción ejecutadas con Node.js
```

Las pruebas Python se conservan dentro del módulo que verifican. Las migraciones
también permanecen junto a sus modelos: Django utiliza sus nombres y dependencias
para actualizar la estructura de la base.

## Qué hace cada tipo de archivo

| Archivo | Responsabilidad | Ejemplo |
|---|---|---|
| `urls.py` | Vincula una dirección con la función que la atiende | `/pedidos/nuevo/` |
| `views.py` | Recibe la solicitud, valida y coordina la respuesta | Crear o avanzar un pedido |
| `models.py` | Define entidades, relaciones y comportamiento asociado | Pedido, ingrediente, receta |
| `forms.py` | Define y valida formularios donde se usan formularios Django | Configuración o ingredientes |
| `templates/` | Renderiza las pantallas | `pedidos/crear_pedido.html` |
| `static/js/` | Maneja interacción en el navegador | Pasos, borrador y mapa |
| `static/css/` | Define presentación y adaptación de pantalla | `sistema.css` |
| `migrations/` | Versiona cambios en tablas y determinadas transformaciones de datos | Incorporación de clientes |
| `tests*.py` y `tests/javascript/` | Comprueban comportamiento | Envío, stock y borradores |

No todos los módulos necesitan todos estos archivos. Reportes y costos consultan
información de otros módulos. Nuevo pedido combina validación de la vista con
interacción JavaScript; no toda su lógica está en un `forms.py`.

## Recorrido para explicar un pedido

1. El navegador solicita `/pedidos/nuevo/`. `entre_brasas/urls.py` deriva a
   `pedidos/urls.py`, que llama a `crear_pedido` en `pedidos/views.py`.
2. La vista prepara productos activos y configuración, y renderiza
   `templates/pedidos/crear_pedido.html`.
3. El usuario completa Cliente, Hamburguesas, Pago y Ubicación.
   `pasos-pedido.js` controla el avance y `borrador-pedido.js` conserva el
   borrador por pestaña. Guardar el borrador no crea un pedido en SQLite.
4. Al confirmar, el navegador envía los datos. La vista vuelve a validarlos y
   guarda cliente, pedido e ítems dentro de una transacción. La validación del
   navegador por sí sola no alcanza.
5. `pedidos/calculos.py` calcula el envío y total. Los precios se copian a los
   ítems para conservar el histórico aunque cambien los precios del menú.
6. Al pasar a preparación, se descuentan ingredientes según las recetas.
   Inventario registra los movimientos. Un pedido entregado cuenta en ventas.

## Archivos que conviene mostrar

| Tema de la defensa | Archivo o carpeta |
|---|---|
| Entidades y relaciones | `pedidos/models.py`, `menu/models.py`, `inventario/models.py` |
| Reglas de envío, total y stock | `pedidos/calculos.py` |
| Validación y guardado del pedido | `pedidos/views.py` |
| Identificación de clientes por teléfono | `pedidos/clientes.py` |
| Interpretación de mensajes pegados | `pedidos/interpretar.py` |
| Comanda | `pedidos/comanda.py` |
| Integración externa Geoapify | `pedidos/mapas.py` y `static/js/mapas-pedido.js` |
| Configuración modificable | `config/models.py`, `config/forms.py` |
| Pruebas de comportamiento | Pruebas Python de cada módulo y `tests/javascript/` |

Las rutas de esta tabla parten de `app/`. El servidor consulta Geoapify y mantiene
la clave fuera del HTML. El navegador muestra el mapa con Leaflet. Se utiliza
internet para consultar mapas; la carga manual de kilómetros sigue disponible.

## Código, datos y herramientas

- `app/db.sqlite3`: datos de desarrollo. La instalación usa
  `%LOCALAPPDATA%\EntreBrasas\db.sqlite3`. La base no se sube a Git.
- `app/venv/`: dependencias instaladas en esta computadora; se reconstruye con
  `requirements.txt`.
- `copias_de_seguridad/`, `cache_mapas/` y `__pycache__/`: respaldos, cachés y
  archivos generados. No son módulos del negocio.
- `.git/`: historial y ramas. Sus hooks son acciones automáticas de Git;
  los archivos terminados en `.sample` son ejemplos inactivos.
- `.claude/` y `.impeccable/`: herramientas y contexto de asistencia al
  desarrollo. No forman parte del funcionamiento de Django.
- `static/vendor/leaflet/` y `static/fonts/`: dependencias visuales con sus
  licencias. Conviene distinguirlas del código propio al presentar el trabajo.

## Cómo defender esta organización

Podés explicarla así: «Dividimos el sistema por áreas del negocio. Django recibe
las solicitudes mediante rutas y vistas, los modelos representan los datos,
las plantillas construyen las pantallas y JavaScript maneja la interacción.
Las cuentas de pedidos están separadas en `calculos.py`, y verificamos las
reglas con pruebas. SQLite permite instalarlo localmente sin administrar un
servidor de base de datos aparte».

Para demostrarlo, recorré un pedido desde la pantalla hasta su guardado y el
descuento de stock. Distinguí lo implementado de las propuestas en `docs/ideas/`
y del trabajo pendiente del plan de mejoras.
