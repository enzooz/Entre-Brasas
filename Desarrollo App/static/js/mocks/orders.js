const ORDERS_MOCK = [
    {
        id: 1,
        cliente: { nombre: "Juan Perez", telefono: "11-5555-1234", direccion: "Av. Libertador 1234" },
        productos: [
            { hamburguesa_id: 1, nombre: "Clasica", cantidad: 2, precio_base: 2500, adicionales: [
                { adicional_id: 1, nombre: "Bacon Extra", precio: 500 },
                { adicional_id: 3, nombre: "Doble Carne", precio: 800 }
            ]}
        ],
        envio: { distancia_km: 3.5, costo_envio: 1750, retiro_local: false },
        observaciones: "Sin cebolla en una de las dos",
        metodo_pago: "Efectivo",
        estado: "Pendiente",
        total: 10500,
        fecha_creacion: "2026-07-21T14:30:00",
        historial: [
            { fecha: "2026-07-21T14:30:00", estado: "Pendiente", observacion: "" }
        ]
    },
    {
        id: 2,
        cliente: { nombre: "Maria Garcia", telefono: "11-6666-5678", direccion: "Calle Principal 456" },
        productos: [
            { hamburguesa_id: 2, nombre: "Especial", cantidad: 1, precio_base: 3200, adicionales: [
                { adicional_id: 1, nombre: "Bacon Extra", precio: 500 }
            ]}
        ],
        envio: { distancia_km: 2, costo_envio: 1000, retiro_local: false },
        observaciones: "",
        metodo_pago: "Transferencia",
        estado: "En preparacion",
        total: 4700,
        fecha_creacion: "2026-07-21T14:15:00",
        historial: [
            { fecha: "2026-07-21T14:15:00", estado: "Pendiente", observacion: "" },
            { fecha: "2026-07-21T14:20:00", estado: "En preparacion", observacion: "" }
        ]
    },
    {
        id: 3,
        cliente: { nombre: "Carlos Lopez", telefono: "11-7777-9012", direccion: "Av. San Martin 789" },
        productos: [
            { hamburguesa_id: 3, nombre: "Veggie", cantidad: 1, precio_base: 2800, adicionales: [] }
        ],
        envio: { distancia_km: 5, costo_envio: 2500, retiro_local: false },
        observaciones: "Entregar rapido porfavor",
        metodo_pago: "Efectivo",
        estado: "En camino",
        total: 5300,
        fecha_creacion: "2026-07-21T13:50:00",
        historial: [
            { fecha: "2026-07-21T13:50:00", estado: "Pendiente", observacion: "" },
            { fecha: "2026-07-21T13:55:00", estado: "En preparacion", observacion: "" },
            { fecha: "2026-07-21T14:10:00", estado: "En camino", observacion: "" }
        ]
    }
];

let _orderNextId = 4;

const OrderService = {
    getAll: (filters = {}) => {
        let orders = [...ORDERS_MOCK];
        if (filters.estado) {
            orders = orders.filter(o => o.estado === filters.estado);
        }
        if (filters.cliente) {
            const search = filters.cliente.toLowerCase();
            orders = orders.filter(o => o.cliente.nombre.toLowerCase().includes(search));
        }
        orders.sort((a, b) => new Date(a.fecha_creacion) - new Date(b.fecha_creacion));
        return orders;
    },
    getActive: () => {
        return ORDERS_MOCK
            .filter(o => ["Pendiente", "En preparacion", "En camino"].includes(o.estado))
            .sort((a, b) => new Date(a.fecha_creacion) - new Date(b.fecha_creacion));
    },
    getFinished: () => {
        return ORDERS_MOCK
            .filter(o => ["Entregado", "Cancelado"].includes(o.estado))
            .sort((a, b) => new Date(b.fecha_creacion) - new Date(a.fecha_creacion));
    },
    getById: (id) => ORDERS_MOCK.find(o => o.id === id),
    create: (data) => {
        const now = new Date().toISOString();
        const newOrder = {
            id: _orderNextId++,
            ...data,
            estado: "Pendiente",
            fecha_creacion: now,
            historial: [{ fecha: now, estado: "Pendiente", observacion: "" }]
        };
        ORDERS_MOCK.push(newOrder);
        return newOrder;
    },
    updateStatus: (id, newStatus, observation = '') => {
        const order = ORDERS_MOCK.find(o => o.id === id);
        if (!order) return null;
        const now = new Date().toISOString();
        order.estado = newStatus;
        order.historial.push({ fecha: now, estado: newStatus, observacion: observation });
        return order;
    },
    cancel: (id, observation = '') => {
        return OrderService.updateStatus(id, "Cancelado", observation);
    },
    getDelivered: () => ORDERS_MOCK.filter(o => o.estado === "Entregado"),
    getCancelled: () => ORDERS_MOCK.filter(o => o.estado === "Cancelado")
};
