# RESUMEN DEL BACKEND — ENTRE BRASAS

## ¿Qué es esto?

Este documento describe todo lo que se implementó en el backend de la aplicación
"Entre Brasas" hasta la fecha. Está escrito de forma sencilla para que todo el
equipo pueda entenderlo.

---

## ¿Qué se hizo?

### 1. Configuración del proyecto

- Se creó el archivo `requirements.txt` con las dependencias necesarias
  (Django y PostgreSQL)
- Se configuró la base de datos para usar PostgreSQL
- Se creó la base de datos "entre_brasas" en PostgreSQL

### 2. Modelos de base de datos

Se crearon las tablas necesarias para guardar toda la información del sistema:

**Menú (Hamburguesas y Adicionales)**
- Cada hamburguesa tiene: nombre, descripción, precio, si incluye papas y si está activa
- Cada adicional tiene: nombre, precio y a qué hamburguesas está asociado
- Los adicionales pueden associarse a múltiples hamburguesas

**Ingredientes**
- Cada ingrediente tiene: nombre, stock actual, unidad de medida (kg, g, L, etc.),
  stock mínimo y precio de última compra
- Se pueden activar/desactivar sin borrar los datos

**Recetas**
- Cada hamburguesa o adicional tiene una "receta" que dice qué ingredientes necesita
  y en qué cantidad (ej: 1 Clásica = 200g carne + 1 pan + 50g lechuga)

**Pedidos**
- Cada pedido tiene: datos del cliente (nombre, teléfono, dirección), productos
  seleccionados con sus adicionales, método de pago, costo de envío, total y estado
- Los estados son: Pendiente → En preparación → En camino → Entregado (o Cancelado)
- Se guarda un historial de cada cambio de estado

**Configuración del sistema**
- Tarifa por kilómetro de envío
- Distancia mínima para cobrar envío
- Costo mínimo de envío
- Costo de mano de obra por hora

### 3. Formularios con validaciones

Se crearon formularios para cada sección que validan:
- Campos obligatorios (no se puede enviar un formulario vacío)
- Nombres duplicados (no se pueden crear dos hamburguesas con el mismo nombre)
- Precios mayores a 0
- Stock mínimo mayor a 0
- Teléfonos con formato válido
- Adicionales asociados a al menos un producto

### 4. Lógica de negocio

**Creación de pedidos:**
- Se calcula automáticamente el costo de envío según la distancia y la configuración
- Si el cliente retira en local, el envío es $0
- Si la distancia es menor a la mínima, no se cobra envío
- Se calcula el total del pedido (productos + adicionales + envío)

**Avance de estado:**
- Pendiente → En preparación → En camino → Entregado
- No se pueden saltar estados ni ir hacia atrás
- Se puede cancelar en cualquier momento antes de entregar

**Descuento automático de stock:**
- Cuando un pedido pasa a "En preparación", se descuenta automáticamente
  el stock de ingredientes según la receta
- Si no hay stock suficiente, muestra un error y no deja avanzar

**Devolución de stock:**
- Si se cancela un pedido que ya descontó stock, aparece una pregunta:
  "¿Desea devolver el stock al inventario?"
- Si dice sí, se devuelve. Si dice no, queda como pérdida

**Movimientos de inventario:**
- Se pueden registrar entradas (compras) y salidas (usos)
- En las salidas, no se puede sacar más stock del disponible
- Cada movimiento se guarda con fecha, hora y motivo

### 5. Seed de datos iniciales

Se cargaron datos de prueba:
- 7 hamburguesas (Clásica, Especial, Veggie, Doble Bacon, Pollo Crispy, BBQ, Hawaiana)
- 17 ingredientes (carne, pan, lechuga, tomate, etc.)
- 5 adicionales (Bacon Extra, Guacamole, Doble Carne, Cheddar Extra, Huevo Frito)
- Recetas para cada hamburguesa (qué ingredientes y cuánto necesita cada una)
- Configuración por defecto (tarifa $500/km, distancia mínima 1km, etc.)

### 6. Superusuario

Se creó un usuario administrador:
- Usuario: admin
- Contraseña: admin123
- Sirve para acceder al panel de administración de Django

---

## ¿Qué se puede hacer ahora?

| Sección | Qué se puede hacer |
|---------|---------------------|
| Hamburguesas | Crear, editar, activar/desactivar |
| Adicionales | Crear, editar, activar/desactivar, asociar a hamburguesas |
| Ingredientes | Crear, editar, activar/desactivar |
| Pedidos | Crear pedidos con productos, adicionales y envío |
| Cola de pedidos | Ver pedidos activos, avanzar estados, cancelar |
| Historial | Ver pedidos entregados y cancelados |
| Inventario | Ver stock, registrar entradas y salidas |
| Recetas | Asociar ingredientes a productos con cantidades |
| Configuración | Modificar tarifa de envío, distancia mínima, etc. |

---

## ¿Qué falta?

- Conectar los templates HTML con los datos del backend (reemplazar los mocks
  de JavaScript por consultas reales a la base de datos)
- Módulo de reportes de ventas
- Módulo de costos y rentabilidad
- Módulo de cierre del día (ver documento "Idea_CierreDelDia.md")

---

## Archivos importantes

| Archivo | Qué hace |
|---------|----------|
| `requirements.txt` | Dependencias del proyecto |
| `entre_brasas/settings.py` | Configuración general |
| `apps/menu/models.py` | Modelos de hamburguesas y adicionales |
| `apps/inventory/models.py` | Modelos de ingredientes, recetas y movimientos |
| `apps/orders/models.py` | Modelos de pedidos e historial |
| `apps/config/models.py` | Modelo de configuración del sistema |
| `apps/orders/services.py` | Lógica de negocio (envío, stock, etc.) |
| `apps/menu/management/commands/seed_data.py` | Datos iniciales de prueba |
