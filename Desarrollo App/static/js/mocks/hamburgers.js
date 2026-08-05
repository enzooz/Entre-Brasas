const HAMBURGERS_MOCK = [
    { id: 1, nombre: "Clasica", descripcion: "Pan, carne, lechuga, tomate, cebolla", precio_base: 2500, incluye_papas: true, activa: true },
    { id: 2, nombre: "Especial", descripcion: "Doble carne, bacon, cheddar, cebolla caramelizada", precio_base: 3200, incluye_papas: false, activa: true },
    { id: 3, nombre: "Veggie", descripcion: "Medallon de verduras, palta, lechuga", precio_base: 2800, incluye_papas: true, activa: true },
    { id: 4, nombre: "Doble Bacon", descripcion: "Doble carne, doble bacon, cheddar, BBQ", precio_base: 3800, incluye_papas: false, activa: true },
    { id: 5, nombre: "Pollo Crispy", descripcion: "Pechuga de pollo empanizada, lechuga, mayonesa", precio_base: 2700, incluye_papas: true, activa: true },
    { id: 6, nombre: "BBQ", descripcion: "Carne, bacon, cebolla crispy, salsa BBQ", precio_base: 3100, incluye_papas: false, activa: true },
    { id: 7, nombre: "Hawaiana", descripcion: "Carne, jamon, pina, queso", precio_base: 2900, incluye_papas: true, activa: true }
];

let _hamburgerNextId = 8;

const HamburgerService = {
    getAll: () => [...HAMBURGERS_MOCK],
    getActive: () => HAMBURGERS_MOCK.filter(h => h.activa),
    getById: (id) => HAMBURGERS_MOCK.find(h => h.id === id),
    create: (data) => {
        const newHamburger = { id: _hamburgerNextId++, ...data, activa: true };
        HAMBURGERS_MOCK.push(newHamburger);
        return newHamburger;
    },
    update: (id, data) => {
        const idx = HAMBURGERS_MOCK.findIndex(h => h.id === id);
        if (idx !== -1) {
            HAMBURGERS_MOCK[idx] = { ...HAMBURGERS_MOCK[idx], ...data };
            return HAMBURGERS_MOCK[idx];
        }
        return null;
    },
    deactivate: (id) => {
        const h = HAMBURGERS_MOCK.find(h => h.id === id);
        if (h) { h.activa = false; return true; }
        return false;
    },
    hasOrders: (id) => false
};
