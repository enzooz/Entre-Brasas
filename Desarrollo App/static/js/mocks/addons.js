const ADDONS_MOCK = [
    { id: 1, nombre: "Bacon Extra", precio: 500, productos_ids: [1, 2, 4, 6], activo: true },
    { id: 2, nombre: "Guacamole", precio: 400, productos_ids: [1, 3, 5], activo: true },
    { id: 3, nombre: "Doble Carne", precio: 800, productos_ids: [1, 3, 5, 7], activo: true },
    { id: 4, nombre: "Cheddar Extra", precio: 300, productos_ids: [1, 2, 3, 4, 5, 6, 7], activo: true },
    { id: 5, nombre: "Huevo Frito", precio: 250, productos_ids: [1, 2, 4, 6], activo: true }
];

let _addonNextId = 6;

const AddonService = {
    getAll: () => [...ADDONS_MOCK],
    getActive: () => ADDONS_MOCK.filter(a => a.activo),
    getById: (id) => ADDONS_MOCK.find(a => a.id === id),
    getByHamburgerId: (hamburgerId) => ADDONS_MOCK.filter(a => a.activo && a.productos_ids.includes(hamburgerId)),
    create: (data) => {
        const newAddon = { id: _addonNextId++, ...data, activo: true };
        ADDONS_MOCK.push(newAddon);
        return newAddon;
    },
    update: (id, data) => {
        const idx = ADDONS_MOCK.findIndex(a => a.id === id);
        if (idx !== -1) {
            ADDONS_MOCK[idx] = { ...ADDONS_MOCK[idx], ...data };
            return ADDONS_MOCK[idx];
        }
        return null;
    },
    deactivate: (id) => {
        const a = ADDONS_MOCK.find(a => a.id === id);
        if (a) { a.activo = false; return true; }
        return false;
    }
};
