# IDEA: MÓDULO "CERRAR EL DÍA"

## ¿Qué es?

Es una pantalla donde el administrador puede ver un resumen completo de lo que
pasó durante el día y "cerrar" la jornada. Al cerrar, se guarda un registro
con todos los datos para poder consultarlos después.

---

## ¿Qué información muestra?

### Resumen de ventas
- Cuánto se vendió en total (en pesos)
- Cuántos pedidos se entregaron
- Cuál es el ticket promedio (cuánto gasta cada cliente en promedio)
- Cuál fue la hamburguesa más pedida

### Métodos de pago
- Cuánto se cobró en efectivo y cuántos pedidos fueron
- Cuánto se cobró por transferencia/QR y cuántos pedidos fueron

### Envíos
- Cuántos pedidos fueron envío a domicilio
- Cuántos pedidos fueron retiro en local
- Cuánto se cobró total en envíos

### Rentabilidad
- Cuánto costaron los ingredientes que se usaron hoy
- Cuál fue la ganancia neta (lo que se vendió menos lo que costaron los ingredientes)

### Pedidos cancelados
- Cuántos pedidos se cancelaron
- Cuál fue el motivo de cada cancelación

### Alertas de inventario
- Qué ingredientes se quedaron sin stock (cantidad = 0)
- Qué ingredientes están por debajo del mínimo

---

## ¿Qué pasa cuando se "Cierra el Día"?

1. Se guarda un registro con todos los datos anteriores (fecha, hora, etc.)
2. Ese registro queda guardado para poder verlo después
3. El día siguiente se puede volver a cerrar

**No se borra nada.** Simplemente se guarda un "snapshot" (foto) de cómo
estuvo el día.

---

## ¿Para qué sirve?

- El dueño puede ver cuánto facturó cada día
- Puede comparar días entre sí (¿cuánto se vendió el lunes vs el martes?)
- Puede saber cuál es la hamburguesa más popular
- Puede controlar si hay ingredientes con stock bajo
- Puede ver cuánto ganó realmente (después de restar costos)
- Tiene un historial de cierres para consulta

---

## Pantalla propuesta

```
┌──────────────────────────────────────────────────────┐
│  CERRAR EL DÍA                                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  RESUMEN DE VENTAS                                   │
│  Total vendido:        $45.000                       │
│  Pedidos entregados:   18                            │
│  Ticket promedio:      $2.500                        │
│  Hamburguesa más vendida: Clásica (8 unidades)       │
│                                                      │
│  MÉTODOS DE PAGO                                     │
│  Efectivo:       $27.000 (11 pedidos)                │
│  Transferencia:  $18.000 (7 pedidos)                 │
│                                                      │
│  ENVÍOS                                              │
│  Envíos a domicilio: 12  │  Costo total: $6.000      │
│  Retiros en local:   6                              │
│                                                      │
│  RENTABILIDAD                                        │
│  Costo ingredientes:  $18.000                        │
│  Ganancia neta:       $27.000                        │
│                                                      │
│  PEDIDOS CANCELADOS (3)                              │
│  #005 - Juan P. - "Cliente no respondió"             │
│  #012 - María G. - "Stock insuficiente"              │
│                                                      │
│  ALERTAS DE INVENTARIO                               │
│  Sin stock: Lechuga (0 kg)                           │
│  Stock bajo: Tomate (3 und, mínimo 5)                │
│                                                      │
│  [Ver Historial de Cierres]   [Cerrar Día]           │
└──────────────────────────────────────────────────────┘
```

---

## Historial de cierres

Se puede ver una lista con todos los cierres anteriores:

| Fecha | Ventas | Pedidos | Ticket | Ganancia |
|-------|--------|---------|--------|----------|
| 04/08/2026 | $45.000 | 18 | $2.500 | $27.000 |
| 03/08/2026 | $38.000 | 15 | $2.533 | $22.000 |
| 02/08/2026 | $52.000 | 22 | $2.363 | $31.000 |

---

## ¿Qué se necesita para implementarlo?

- Una nueva tabla para guardar los cierres
- Una pantalla que calcule y muestre los datos del día
- Un botón para "Cerrar" que guarde el registro
- Una pantalla de historial con los cierres anteriores
- Un enlace en el menú de navegación

---

## Estado

Esta es una **idea/propuesta**. Falta implementar.
