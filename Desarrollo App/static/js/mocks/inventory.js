const INVENTORY_MOVEMENTS_MOCK = [
    { id: 1, ingrediente_id: 1, ingrediente_nombre: "Carne molida", tipo: "entrada", cantidad: 10, unidad: "kg", motivo: "Compra semanal", fecha: "2026-07-21T10:00:00" },
    { id: 2, ingrediente_id: 1, ingrediente_nombre: "Carne molida", tipo: "salida", cantidad: 5, unidad: "kg", motivo: "Pedido #1", fecha: "2026-07-21T14:30:00" },
    { id: 3, ingrediente_id: 2, ingrediente_nombre: "Pan de hamburguesa", tipo: "entrada", cantidad: 30, unidad: "unidades", motivo: "Compra diaria", fecha: "2026-07-21T09:00:00" },
    { id: 4, ingrediente_id: 3, ingrediente_nombre: "Lechuga", tipo: "salida", cantidad: 1, unidad: "kg", motivo: "Uso general", fecha: "2026-07-21T12:00:00" }
];

let _movementNextId = 5;

const InventoryService = {
    getMovements: (filters = {}) => {
        let movements = [...INVENTORY_MOVEMENTS_MOCK];
        if (filters.ingrediente_id) {
            movements = movements.filter(m => m.ingrediente_id === filters.ingrediente_id);
        }
        if (filters.tipo) {
            movements = movements.filter(m => m.tipo === filters.tipo);
        }
        if (filters.fecha_desde) {
            movements = movements.filter(m => new Date(m.fecha) >= new Date(filters.fecha_desde));
        }
        if (filters.fecha_hasta) {
            movements = movements.filter(m => new Date(m.fecha) <= new Date(filters.fecha_hasta));
        }
        movements.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
        return movements;
    },
    addEntry: (ingredienteId, cantidad, motivo) => {
        const ingredient = INGREDIENTS_MOCK.find(i => i.id === ingredienteId);
        if (!ingredient) return null;
        ingredient.stock_actual += cantidad;
        const movement = {
            id: _movementNextId++,
            ingrediente_id: ingredienteId,
            ingrediente_nombre: ingredient.nombre,
            tipo: "entrada",
            cantidad,
            unidad: ingredient.unidad,
            motivo,
            fecha: new Date().toISOString()
        };
        INVENTORY_MOVEMENTS_MOCK.push(movement);
        return movement;
    },
    addExit: (ingredienteId, cantidad, motivo) => {
        const ingredient = INGREDIENTS_MOCK.find(i => i.id === ingredienteId);
        if (!ingredient || ingredient.stock_actual < cantidad) return null;
        ingredient.stock_actual -= cantidad;
        const movement = {
            id: _movementNextId++,
            ingrediente_id: ingredienteId,
            ingrediente_nombre: ingredient.nombre,
            tipo: "salida",
            cantidad,
            unidad: ingredient.unidad,
            motivo,
            fecha: new Date().toISOString()
        };
        INVENTORY_MOVEMENTS_MOCK.push(movement);
        return movement;
    },
    addAutomaticExit: (ingredienteId, cantidad, motivo) => {
        return InventoryService.addExit(ingredienteId, cantidad, motivo);
    },
    addAutomaticEntry: (ingredienteId, cantidad, motivo) => {
        return InventoryService.addEntry(ingredienteId, cantidad, motivo);
    }
};
