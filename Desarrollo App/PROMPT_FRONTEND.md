# PROMPT — SPEC DRIVEN DEVELOPMENT: FRONTEND

## Entre Brasas — Hamburguesería: Aplicación Web de Gestión

---

### CONTEXTO Y OBJETIVO

Sos un desarrollador senior. Tu tarea es construir el **frontend completo** de una aplicación web de gestión interna para una hamburguesería llamada "Entre Brasas".

**Stack obligatorio:**
- Python 3.x + Django Framework
- Django Templates (HTML + Jinja2) para server-side rendering
- JavaScript vanilla mínimo y únicamente cuando sea estrictamente necesario para interacciones en tiempo real (ej: cálculo de totales en el formulario de pedido). Todo lo demás se resuelve server-side con Django.
- Sin frameworks CSS (sin Tailwind, Bootstrap, etc.)
- Sin estilos visuales (HTML crudo funcional)

**Enfoque:** Este prompt cubre **ÚNICAMENTE el frontend**. Los datos son mocks hardcodeados. El backend y la base de datos se integrarán en una fase posterior. Todo el código debe estar preparado para ese día.

**Moneda:** Pesos argentinos (ARS). Formato: `$ 1.250,00`

**Idioma:** Interfaz 100% en español.

**Público target:** Un único administrador que opera desde una PC de escritorio en el local.

---

### ESTRUCTURA DEL PROYECTO

```
entre_brasas/
├── manage.py
├── requirements.txt
├── entre_brasas/                  # Proyecto Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── templates/                     # Templates globales
│   ├── base.html                  # Layout base (sidebar, header, contenido)
│   └── components/                # Componentes reutilizables
│       ├── navbar.html
│       ├── sidebar.html
│       ├── modal.html
│       ├── toast.html
│       ├── table.html
│       ├── form_field.html
│       ├── empty_state.html
│       └── loading_spinner.html
│
├── static/
│   └── js/
│       ├── app.js                 # Inicialización global
│       ├── mocks/                 # Datos mock por módulo
│       │   ├── hamburgers.js
│       │   ├── addons.js
│       │   ├── ingredients.js
│       │   ├── orders.js
│       │   ├── inventory.js
│       │   └── config.js
│       ├── services/              # Capa de abstracción para backend futuro
│       │   ├── api.js
│       │   ├── hamburger_service.js
│       │   ├── addon_service.js
│       │   ├── ingredient_service.js
│       │   ├── order_service.js
│       │   ├── inventory_service.js
│       │   ├── report_service.js
│       │   └── config_service.js
│       └── modules/               # Lógica JS por pantalla
│           ├── create_order.js
│           ├── order_queue.js
│           ├── order_detail.js
│           ├── manage_hamburgers.js
│           ├── manage_addons.js
│           ├── manage_ingredients.js
│           ├── inventory.js
│           ├── reports.js
│           ├── costs.js
│           └── admin_panel.js
│
├── apps/
│   ├── orders/                    # Módulo de pedidos
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── menu/                      # Módulo hamburguesas, adicionales
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── inventory/                 # Módulo inventario
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── reports/                   # Módulo reportes
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── costs/                     # Módulo costos/rentabilidad
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   └── views.py
│   └── config/                    # Panel de administración
│       ├── __init__.py
│       ├── urls.py
│       └── views.py
```

---

### CAPA DE SERVICIOS (ABSTRACCIÓN PARA BACKEND FUTURO)

Cada módulo tiene un archivo `*_service.js` que expone funciones con la misma interfaz que luego tendrá la API real. Por ahora, estos servicios leen de los mocks. Cuando se implemente el backend, solo se reemplaza el contenido interno de cada función.

**Regla estricta:** Ningún módulo JS accede directamente a los mocks. Siempre pasa por el servicio.

---

### ESPECIFICACIÓN DE PANTALLAS

---

#### PANTALLA 1 — CREAR PEDIDO

**URL:** `/pedidos/nuevo/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Nuevo Pedido"                         │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  ┌─── Datos del Cliente ──────────────────────┐  │
│           │  │  Nombre *    [________________]            │  │
│           │  │  Teléfono *  [________________]            │  │
│           │  │  Dirección * [________________]            │  │
│           │  │  Observaciones [________________]          │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Productos ─────────────────────────────┐  │
│           │  │  [Seleccionar hamburguesa ▼]  [Cantidad]   │  │
│           │  │  ┌─ Adicionales disponibles ─────────┐    │  │
│           │  │  │ ☐ Adicional 1 ($500)               │    │  │
│           │  │  │ ☐ Adicional 2 ($300)               │    │  │
│           │  │  └───────────────────────────────────┘    │  │
│           │  │  [+ Agregar otro producto]                  │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Envío ────────────────────────────────┐  │
│           │  │  ¿Retira en local? [Sí/No]               │  │
│           │  │  Distancia (km): [_______]                │  │
│           │  │  Costo envío: $ 0 (calculado)             │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Resumen ──────────────────────────────┐  │
│           │  │  Subtotal productos:   $ X               │  │
│           │  │  Subtotal adicionales: $ X               │  │
│           │  │  Costo envío:          $ X               │  │
│           │  │  TOTAL:                $ X               │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  Método de pago *: [Efectivo ▼] [Transferencia] │
│           │                                                 │
│           │  [Cancelar]                    [Crear Pedido]    │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- El select de hamburguesas muestra solo las activas.
- Al seleccionar una hamburguesa, se cargan dinámicamente los adicionales asociados.
- El cálculo de totales es en tiempo real al modificar cantidades o adicionales.
- Al confirmar, el pedido se guarda con estado "Pendiente" y redirige a la cola.
- **Validaciones:** nombre, teléfono, dirección y método de pago son obligatorios. Debe haber al menos 1 producto.

---

#### PANTALLA 2 — COLA DE PEDIDOS (FIFO)

**URL:** `/pedidos/cola/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Cola de Pedidos"                      │
│           ├──────────────────────────────────────────────────┤
│           │  [Buscar por cliente...]  [Filtrar: Todos ▼]    │
│           │                                                 │
│           │  ┌─────────────────┐  ┌─────────────────┐       │
│           │  │ Pendiente        │  │ En preparación   │       │
│           │  │ Juan Pérez      │  │ María García    │       │
│           │  │ 2 Clásica       │  │ 1 Especial +bacon│       │
│           │  │ Total: $10.500  │  │ Total: $4.200   │       │
│           │  │ 14:30           │  │ 14:15           │       │
│           │  │ [▶ En preparación]│ │ [▶ En camino]   │       │
│           │  └─────────────────┘  └─────────────────┘       │
│           │                                                 │
│           │  ┌─────────────────┐                             │
│           │  │ En camino        │                             │
│           │  │ Carlos López    │                             │
│           │  │ 1 Veggie        │                             │
│           │  │ Total: $3.800   │                             │
│           │  │ 13:50           │                             │
│           │  │ [▶ Entregado]   │                             │
│           │  └─────────────────┘                             │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- Muestra solo pedidos con estado Pendiente, En preparación o En camino.
- Orden FIFO: más antiguo primero.
- Cada tarjeta tiene un botón que avanza al siguiente estado.
- Filtrado por nombre de cliente y por estado.
- Pedidos Entregados/Cancelados NO aparecen aquí.

---

#### PANTALLA 3 — DETALLE / GESTIONAR PEDIDO

**URL:** `/pedidos/<id>/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Pedido #001"     [← Volver a la cola] │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  ┌─── Datos del Cliente ──────────────────────┐  │
│           │  │  Nombre: Juan Pérez                        │  │
│           │  │  Teléfono: 11-5555-1234                    │  │
│           │  │  Dirección: Av. Libertador 1234            │  │
│           │  │  Observaciones: Sin cebolla en una de las  │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Productos ─────────────────────────────┐  │
│           │  │  #  Producto      Cant  Precio  Subtotal  │  │
│           │  │  1  Clásica       2     $2.500  $5.000    │  │
│           │  │     └ Bacon Extra 1     $500    $500      │  │
│           │  │     └ Doble carne 1     $800    $800      │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Costos ────────────────────────────────┐  │
│           │  │  Productos:  $5.000                        │  │
│           │  │  Adicionales: $1.300                       │  │
│           │  │  Envío:       $1.750                       │  │
│           │  │  TOTAL:       $8.050                       │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Estado ────────────────────────────────┐  │
│           │  │  Estado actual: Pendiente                  │  │
│           │  │  Observación: [________________]           │  │
│           │  │  [Avanzar estado]  [Cancelar pedido]       │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Historial ─────────────────────────────┐  │
│           │  │  21/07 14:30 - Creado                     │  │
│           │  │  21/07 14:35 - Cambiado a En preparación  │  │
│           │  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- Muestra toda la información del pedido.
- Si se cancela estando en "Pendiente": se marca como Cancelado, sin impacto en inventario.
- Si se cancela estando en "En preparación" o "En camino": se muestra un popup preguntando si desea devolver el stock.
- El historial muestra cada cambio de estado con fecha, hora y observación opcional.

---

#### PANTALLA 4 — GESTIONAR HAMBURGUESAS

**URL:** `/menu/hamburguesas/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Hamburguesas"   [+ Nueva Hamburguesa] │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  Nombre          Descripción       Precio  Papas│
│           │  ─────────────────────────────────────────────  │
│           │  Clásica         Pan, carne...     $2.500  Sí   │
│           │  [Editar] [Desactivar]                          │
│           │  Especial        Doble carne...    $3.200  No   │
│           │  [Editar] [Desactivar]                          │
│           │  Veggie          Medallón...       $2.800  Sí   │
│           │  [Editar] [Desactivar]                          │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- CRUD completo: Crear, Editar, Listar. Eliminación lógica.
- Formulario: nombre (obligatorio), descripción (obligatorio), precio base (> 0), incluye papas (sí/no).
- **Restricción:** No duplicar nombres. No desactivar hamburguesas con pedidos asociados.

---

#### PANTALLA 5 — GESTIONAR ADICIONALES

**URL:** `/menu/adicionales/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Adicionales"     [+ Nuevo Adicional]  │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  Nombre          Precio   Asociado a      Estado│
│           │  ─────────────────────────────────────────────  │
│           │  Bacon Extra     $500     Clásica, Esp.  Activo │
│           │  [Editar] [Desactivar]                          │
│           │  Doble carne     $800     Especial       Activo │
│           │  [Editar] [Desactivar]                          │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- CRUD completo. Eliminación lógica.
- Formulario: nombre (obligatorio), precio (> 0), productos asociados (select múltiple, al menos 1).

---

#### PANTALLA 6 — GESTIONAR INGREDIENTES

**URL:** `/inventario/ingredientes/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Ingredientes"   [+ Nuevo Ingrediente] │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  Nombre          Stock   Unidad  Mínimo  Estado │
│           │  ─────────────────────────────────────────────  │
│           │  Carne molida    15 kg    kg      5 kg   Activo │
│           │  [Editar] [Desactivar]                          │
│           │  Pan             50 und   und     10     Activo │
│           │  [Editar] [Desactivar]                          │
│           │  Lechuga         2 kg     kg      3 kg   Activo │
│           │  [Editar] [Desactivar]                          │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- CRUD completo. Eliminación lógica.
- Formulario: nombre (obligatorio), stock inicial (numérico), unidad (kg/g/L/mL/unidades), stock mínimo (> 0).
- El stock actual solo se modifica vía movimientos de inventario.

---

#### PANTALLA 7 — INVENTARIO (MOVIMIENTOS)

**URL:** `/inventario/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Inventario"                           │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  ┌─── Panel de ingredientes ─────────────────┐  │
│           │  │  Carne molida: 15 kg  [＋ Entrada] [− Salida]│ │
│           │  │  Pan: 50 und         [＋ Entrada] [− Salida]│ │
│           │  │  Lechuga: 2 kg       [＋ Entrada] [− Salida]│ │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Historial de movimientos ──────────────┐  │
│           │  │  Fecha     │ Ingrediente  │ Tipo  │ Cant  │  │
│           │  │  21/07 10:00│ Carne molida │ Entr. │ +10kg │  │
│           │  │  21/07 14:00│ Carne molida │ Salida│ -5kg  │  │
│           │  └────────────────────────────────────────────┘  │
│           │  [Filtrar: ingrediente ▼] [Tipo: Todos ▼]       │
│           │  [Rango fechas: Desde ___ Hasta ___]             │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- Vista principal con acceso rápido a entradas/salidas.
- Modal con formulario para registrar movimientos.
- **Validación en salida:** No permite sacar más stock del disponible.
- Historial con filtros: ingrediente, tipo, rango de fechas.

---

#### PANTALLA 8 — REPORTES DE VENTAS

**URL:** `/reportes/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Reportes de Ventas"                   │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  [Desde: __/__/__] [Hasta: __/__/__] [Filtrar]  │
│           │                                                 │
│           │  ┌─── Resumen ─────────────────────────────┐    │
│           │  │  Ventas totales: $125.000               │    │
│           │  │  Pedidos: 42  │ Ticket promedio: $2.976 │    │
│           │  │  Envíos: $18.500                         │    │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Ventas por día ──────────────────────┐    │
│           │  │  [Tabla con Totales diarios]             │    │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Por método de pago ──────────────────┐    │
│           │  │  Efectivo: $75.000 (30 pedidos)         │    │
│           │  │  Transferencia: $50.000 (12 pedidos)    │    │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Top productos ───────────────────────┐    │
│           │  │  1. Clásica      - 25 uds - $62.500    │    │
│           │  │  2. Especial     - 12 uds - $38.400    │    │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Top adicionales ─────────────────────┐    │
│           │  │  1. Bacon Extra  - 18 veces             │    │
│           │  │  2. Doble carne  - 10 veces             │    │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Comparación ─────────────────────────┐    │
│           │  │  Período actual vs. anterior             │    │
│           │  │  [Tabla comparativa]                     │    │
│           │  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- Solo incluye pedidos con estado Entregado.
- Filtro por rango de fechas.
- Ticket promedio = Total ventas / Cantidad de pedidos.
- Comparación: período seleccionado vs. período anterior.

---

#### PANTALLA 9 — COSTOS Y RENTABILIDAD

**URL:** `/costos/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Costos y Rentabilidad"                │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  [Filtrar por producto: Todos ▼]                 │
│           │                                                 │
│           │  Producto │ Costo Ingred. │ Costo MO │ Total    │
│           │  Precio   │ Margen %      │ Ganancia $          │
│           │  ─────────────────────────────────────────────  │
│           │  Clásica  │ $800          │ $200     │ $1.000   │
│           │           │ $2.500        │ 150%     │ $1.500   │
│           │  ─────────────────────────────────────────────  │
│           │                                                 │
│           │  ┌─── Resumen general ──────────────────────┐   │
│           │  │  Margen promedio del menú: 135%          │   │
│           │  │  Producto más rentable: Veggie           │   │
│           │  │  Producto menos rentable: Doble bacon    │   │
│           │  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- Costo de ingredientes = suma(cantidad × precio unitario).
- Costo de mano de obra = costo configurable × tiempo estimado.
- Margen de ganancia = ((Precio Venta - Costo Total) / Costo Total) × 100.

---

#### PANTALLA 10 — ASOCIACIÓN INGREDIENTE-PRODUCTO

**URL:** `/config/recetas/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Recetas (Ingrediente ↔ Producto)"     │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  Seleccionar producto: [Clásica ▼]              │
│           │                                                 │
│           │  Ingrediente       │ Cantidad │ Costo            │
│           │  ─────────────────────────────────────────────  │
│           │  Carne molida      │ 200 g    │ $320             │
│           │  Pan               │ 1 und    │ $80              │
│           │  Lechuga           │ 50 g     │ $40              │
│           │  Tomate            │ 2 rodajas│ $60              │
│           │  Cebolla           │ 1 porc.  │ $20              │
│           │                    │ TOTAL:   │ $520             │
│           │                                                 │
│           │  [+ Agregar ingrediente]                        │
│           │                                                 │
│           │  Precio de venta: $2.500                         │
│           │  Costo total (ing + MO): $720                    │
│           │  Margen de ganancia: 247%                        │
│           │  Ganancia neta por unidad: $1.780                │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- Permite configurar ingredientes de cada producto.
- Calcula automáticamente costo de receta, costo total con mano de obra, margen.

---

#### PANTALLA 11 — PANEL DE ADMINISTRACIÓN

**URL:** `/admin/config/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Panel de Administración"              │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  ┌─── Configuración de envío ───────────────┐  │
│           │  │  Tarifa por km:    [$ 500    ]            │  │
│           │  │  Distancia mínima: [1 km     ]            │  │
│           │  │  Costo mínimo:     [$ 1000   ]            │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  ┌─── Mano de obra ─────────────────────────┐  │
│           │  │  Costo hora: [$ 2500]  Costo min: [$ 42] │  │
│           │  └────────────────────────────────────────────┘  │
│           │                                                 │
│           │  [Guardar cambios]                              │
│           │                                                 │
│           │  ── Accesos directos ──                         │
│           │  [Gestionar Hamburguesas]                       │
│           │  [Gestionar Adicionales]                        │
│           │  [Gestionar Ingredientes]                       │
│           │  [Configurar Recetas]                           │
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- Formulario con configuración del sistema.
- Los valores se guardan en localStorage por ahora.

---

#### PANTALLA 12 — HISTORIAL DE PEDIDOS

**URL:** `/pedidos/historial/`

**Wireframe:**
```
┌──────────────────────────────────────────────────────────────┐
│  Sidebar  │  Header: "Historial de Pedidos"                 │
│           ├──────────────────────────────────────────────────┤
│           │                                                 │
│           │  [Buscar por cliente...]  [Estado: Todos ▼]     │
│           │  [Desde: __/__/__] [Hasta: __/__/__]            │
│           │                                                 │
│           │  #001 │ Juan Pérez  │ Entregado  │ $10.500 │ 21/07│
│           │  #002 │ María García│ Cancelado  │ $3.200  │ 21/07│
│           │                                                 │
│           │  Al hacer clic → Detalle del pedido (Pantalla 3)│
└──────────────────────────────────────────────────────────────┘
```

**Comportamiento:**
- Solo pedidos Entregados o Cancelados.
- Ordenados por fecha (más reciente primero).
- Filtrado: nombre, estado, rango de fechas.

---

### MOCKS INICIALES

**Hamburguesas:**
```javascript
[
  { id: 1, nombre: "Clásica", descripcion: "Pan, carne, lechuga, tomate, cebolla", precio_base: 2500, incluye_papas: true, activa: true },
  { id: 2, nombre: "Especial", descripcion: "Doble carne, bacon, cheddar, cebolla caramelizada", precio_base: 3200, incluye_papas: false, activa: true },
  { id: 3, nombre: "Veggie", descripcion: "Medallón de verduras, palta, lechuga", precio_base: 2800, incluye_papas: true, activa: true },
  { id: 4, nombre: "Doble Bacon", descripcion: "Doble carne, doble bacon, cheddar, BBQ", precio_base: 3800, incluye_papas: false, activa: true },
  { id: 5, nombre: "Pollo Crispy", descripcion: "Pechuga de pollo empanizada, lechuga, mayonesa", precio_base: 2700, incluye_papas: true, activa: true },
  { id: 6, nombre: "BBQ", descripcion: "Carne, bacon, cebolla crispy, salsa BBQ", precio_base: 3100, incluye_papas: false, activa: true },
  { id: 7, nombre: "Hawaiana", descripcion: "Carne, jamón, piña, queso", precio_base: 2900, incluye_papas: true, activa: true }
]
```

**Adicionales:**
```javascript
[
  { id: 1, nombre: "Bacon Extra", precio: 500, productos_ids: [1, 2, 4, 6], activo: true },
  { id: 2, nombre: "Guacamole", precio: 400, productos_ids: [1, 3, 5], activo: true },
  { id: 3, nombre: "Doble Carne", precio: 800, productos_ids: [1, 3, 5, 7], activo: true },
  { id: 4, nombre: "Cheddar Extra", precio: 300, productos_ids: [1, 2, 3, 4, 5, 6, 7], activo: true },
  { id: 5, nombre: "Huevo Frito", precio: 250, productos_ids: [1, 2, 4, 6], activo: true }
]
```

**Ingredientes:**
```javascript
[
  { id: 1, nombre: "Carne molida", stock_actual: 15, unidad: "kg", stock_minimo: 5, precio_compra: 1600, activo: true },
  { id: 2, nombre: "Pan de hamburguesa", stock_actual: 50, unidad: "unidades", stock_minimo: 10, precio_compra: 80, activo: true },
  { id: 3, nombre: "Lechuga", stock_actual: 2, unidad: "kg", stock_minimo: 3, precio_compra: 800, activo: true },
  { id: 4, nombre: "Tomate", stock_actual: 8, unidad: "unidades", stock_minimo: 5, precio_compra: 30, activo: true },
  { id: 5, nombre: "Cebolla", stock_actual: 6, unidad: "unidades", stock_minimo: 4, precio_compra: 20, activo: true },
  { id: 6, nombre: "Bacon", stock_actual: 3, unidad: "kg", stock_minimo: 2, precio_compra: 3200, activo: true },
  { id: 7, nombre: "Cheddar", stock_actual: 2, unidad: "kg", stock_minimo: 1, precio_compra: 2800, activo: true },
  { id: 8, nombre: "Palta", stock_actual: 5, unidad: "unidades", stock_minimo: 3, precio_compra: 200, activo: true },
  { id: 9, nombre: "Pollo (pechuga)", stock_actual: 8, unidad: "kg", stock_minimo: 3, precio_compra: 2200, activo: true },
  { id: 10, nombre: "Mayonesa", stock_actual: 2, unidad: "L", stock_minimo: 1, precio_compra: 1200, activo: true },
  { id: 11, nombre: "Salsa BBQ", stock_actual: 1.5, unidad: "L", stock_minimo: 0.5, precio_compra: 1500, activo: true },
  { id: 12, nombre: "Cebolla crispy", stock_actual: 1, unidad: "kg", stock_minimo: 0.5, precio_compra: 2000, activo: true },
  { id: 13, nombre: "Jamón", stock_actual: 2, unidad: "kg", stock_minimo: 1, precio_compra: 1800, activo: true },
  { id: 14, nombre: "Piña", stock_actual: 4, unidad: "unidades", stock_minimo: 2, precio_compra: 150, activo: true },
  { id: 15, nombre: "Huevo", stock_actual: 30, unidad: "unidades", stock_minimo: 12, precio_compra: 25, activo: true },
  { id: 16, nombre: "Medallón de verduras", stock_actual: 10, unidad: "unidades", stock_minimo: 5, precio_compra: 350, activo: true },
  { id: 17, nombre: "Queso", stock_actual: 3, unidad: "kg", stock_minimo: 1.5, precio_compra: 2400, activo: true }
]
```

**Configuración:**
```javascript
{ tarifa_km: 500, distancia_minima: 1, costo_minimo_envio: 1000, costo_hora_mano_obra: 2500 }
```

---

### REGLAS GENERALES

1. **Eliminación lógica:** Ninguna entidad se elimina físicamente. Se marca como `activa: false`.

2. **Fechas:** Formato `DD/MM/YYYY HH:mm`.

3. **Estados de pedido:**
   - Pendiente
   - En preparación
   - En camino
   - Entregado
   - Cancelado

4. **Stock bajo:** Ingrediente resaltado cuando `stock_actual < stock_minimo`.

5. **Cálculos en tiempo real:** Los totales en formularios de pedido se recalculan al modificar cantidades o seleccionar adicionales.

6. **Sin autenticación:** No hay login. La app se accede directamente por URL.

7. **Orden FIFO:** La cola de pedidos siempre muestra los más antiguos primero.

8. **Validaciones de formulario:** Todos los campos obligatorios deben validarse antes del submit.

---

### CHECKLIST DE IMPLEMENTACIÓN

- [ ] Proyecto Django creado con estructura de apps
- [ ] base.html con sidebar y layout
- [ ] Servicios JS para cada módulo
- [ ] Mocks de datos
- [ ] Pantalla 1: Crear Pedido
- [ ] Pantalla 2: Cola FIFO
- [ ] Pantalla 3: Detalle Pedido
- [ ] Pantalla 4: CRUD Hamburguesas
- [ ] Pantalla 5: CRUD Adicionales
- [ ] Pantalla 6: CRUD Ingredientes
- [ ] Pantalla 7: Inventario con movimientos
- [ ] Pantalla 8: Reportes de Ventas
- [ ] Pantalla 9: Costos y Rentabilidad
- [ ] Pantalla 10: Asociación Ingrediente-Producto
- [ ] Pantalla 11: Panel de Administración
- [ ] Pantalla 12: Historial de Pedidos
- [ ] Validaciones en todos los formularios
- [ ] Funcionalidad completa sin backend
