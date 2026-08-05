const INGREDIENTS_MOCK = [
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
    { id: 13, nombre: "Jamon", stock_actual: 2, unidad: "kg", stock_minimo: 1, precio_compra: 1800, activo: true },
    { id: 14, nombre: "Pina", stock_actual: 4, unidad: "unidades", stock_minimo: 2, precio_compra: 150, activo: true },
    { id: 15, nombre: "Huevo", stock_actual: 30, unidad: "unidades", stock_minimo: 12, precio_compra: 25, activo: true },
    { id: 16, nombre: "Medallon de verduras", stock_actual: 10, unidad: "unidades", stock_minimo: 5, precio_compra: 350, activo: true },
    { id: 17, nombre: "Queso", stock_actual: 3, unidad: "kg", stock_minimo: 1.5, precio_compra: 2400, activo: true }
];

let _ingredientNextId = 18;

const IngredientService = {
    getAll: () => [...INGREDIENTS_MOCK],
    getActive: () => INGREDIENTS_MOCK.filter(i => i.activo),
    getById: (id) => INGREDIENTS_MOCK.find(i => i.id === id),
    create: (data) => {
        const newIngredient = { id: _ingredientNextId++, ...data, activo: true };
        INGREDIENTS_MOCK.push(newIngredient);
        return newIngredient;
    },
    update: (id, data) => {
        const idx = INGREDIENTS_MOCK.findIndex(i => i.id === id);
        if (idx !== -1) {
            INGREDIENTS_MOCK[idx] = { ...INGREDIENTS_MOCK[idx], ...data };
            return INGREDIENTS_MOCK[idx];
        }
        return null;
    },
    deactivate: (id) => {
        const i = INGREDIENTS_MOCK.find(i => i.id === id);
        if (i) { i.activo = false; return true; }
        return false;
    },
    addStock: (id, quantity) => {
        const i = INGREDIENTS_MOCK.find(i => i.id === id);
        if (i) { i.stock_actual += quantity; return true; }
        return false;
    },
    removeStock: (id, quantity) => {
        const i = INGREDIENTS_MOCK.find(i => i.id === id);
        if (i && i.stock_actual >= quantity) {
            i.stock_actual -= quantity;
            return true;
        }
        return false;
    },
    getLowStock: () => INGREDIENTS_MOCK.filter(i => i.activo && i.stock_actual < i.stock_minimo)
};
