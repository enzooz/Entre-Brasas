const CONFIG_MOCK = {
    tarifa_km: 500,
    distancia_minima: 1,
    costo_minimo_envio: 1000,
    costo_hora_mano_obra: 2500
};

const ConfigService = {
    get: () => ({ ...CONFIG_MOCK }),
    update: (data) => {
        Object.assign(CONFIG_MOCK, data);
        return { ...CONFIG_MOCK };
    }
};
