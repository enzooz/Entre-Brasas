const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/js/mapas-pedido.js'), 'utf8');
const geometry = {type: 'MultiLineString', coordinates: [[[-58.992536, -27.455266], [-58.9865, -27.4511]]]};
const result = {direccion: 'Plaza, Resistencia', latitud: -27.4511, longitud: -58.9865, aproximada: true};
const route = {distancia_km: '1.3', distancia_metros: 1340, geometria: geometry};

function setup({enabled = true, restored = '', address = '', distance = ''} = {}) {
    function node(value = '') {
        const classes = new Set(), events = {};
        return {value, hidden: true, disabled: false, textContent: '', children: [], dataset: {}, events,
            classList: {contains: c => classes.has(c), add: c => classes.add(c), toggle(c, on) {if(on) classes.add(c); else classes.delete(c);}},
            setAttribute() {}, appendChild(child) {this.children.push(child);}, replaceChildren() {this.children = [];},
            querySelectorAll() {return this.children;}, addEventListener(t, fn) {(events[t] ||= []).push(fn);},
            fire(t, event = {}) {return (events[t] || []).map(fn => fn(event));}, focus() {this.focused = true;}};
    }
    const ids = Object.fromEntries(['formPedido','clienteDireccion','distancia','ubicacionPedido','buscarDireccion','resultadosDirecciones',
        'estadoMapa','detalleRecorrido','mostrarMapa','panelMapa','paso-entrega'].map(id => [id, node()]));
    ids.clienteDireccion.value = address; ids.distancia.value = distance; ids.ubicacionPedido.value = restored;
    ids.buscarDireccion.dataset.url = '/pedidos/mapas/buscar/';
    const body = node(), calls = [], observers = [], windowEvents = {};
    let delivery = true;
    ids.formPedido.querySelector = s => s.includes('csrf') ? {value:'csrf-de-prueba'} : delivery ? {value:'false'} : null;
    const document = node();
    document.body = body; document.getElementById = id => ids[id]; document.createElement = () => node();
    document.querySelector = () => ({dataset: {routeUrl: '/pedidos/mapas/recorrido/'}});
    document.dispatchEvent = event => document.fire(event.type, event);
    const window = {addEventListener(t,fn) {windowEvents[t] = fn;}, setTimeout() {return 1;}, clearTimeout() {}};
    const data = {mapas: {habilitado: enabled, origen: [-27.455266,-58.992536]}};
    const fetch = (url, options) => new Promise(resolve => calls.push({url, options, resolve}));
    vm.runInNewContext(source, {document, window, DATOS: data, fetch, AbortController,
        Event: class {constructor(type) {this.type = type;}}, MutationObserver: class {constructor(fn) {observers.push(fn);} observe() {}},
        mostrarLinkMaps() {}, calcularTotal() {document.dispatchEvent({type:'pedido:actualizado'});}});
    document.fire('DOMContentLoaded');
    async function reply(index, payload, ok = true) {calls[index].resolve({ok, json: async () => payload}); await new Promise(setImmediate);}
    return {ids, calls, reply, document, body, observers, windowEvents,
        pickup() {delivery = false; ids.formPedido.fire('change');}};
}

test('escribir no consulta; botón hace una consulta con CSRF y evita doble clic', async () => {
    const ui = setup(); ui.ids.clienteDireccion.value = 'Plaza, Resistencia';
    ui.ids.clienteDireccion.fire('input'); assert.equal(ui.calls.length, 0);
    ui.ids.buscarDireccion.fire('click'); ui.ids.buscarDireccion.fire('click');
    assert.equal(ui.calls.length, 1);
    assert.equal(ui.calls[0].options.headers['X-CSRFToken'], 'csrf-de-prueba');
    assert.deepEqual(JSON.parse(ui.calls[0].options.body), {texto: 'Plaza, Resistencia'});
    await ui.reply(0, {resultados:[result]});
    assert.equal(ui.ids.resultadosDirecciones.children.length, 1);
    assert.equal(ui.ids.buscarDireccion.disabled, false);
});

async function choose(ui) {
    ui.ids.clienteDireccion.value = 'Plaza, Resistencia'; ui.ids.clienteDireccion.fire('input');
    ui.ids.buscarDireccion.fire('click'); await ui.reply(0, {resultados:[result]});
    ui.ids.resultadosDirecciones.children[0].fire('click');
    assert.equal(ui.calls.length, 2);
}

test('seleccionar destino calcula una ruta, km con un decimal y conserva metros en borrador', async () => {
    const ui = setup(); await choose(ui); await ui.reply(1, route);
    assert.equal(ui.ids.distancia.value, '1.3');
    const saved = JSON.parse(ui.ids.ubicacionPedido.value);
    assert.equal(saved.metros, 1340); assert.equal(saved.km, '1.3');
    assert.equal(JSON.stringify(saved).includes('csrf'), false);
    assert.match(ui.ids.detalleRecorrido.textContent, /1,3 km/);
    ui.ids.clienteDireccion.value = 'Otra calle'; ui.ids.clienteDireccion.fire('input');
    assert.equal(ui.ids.distancia.value, ''); assert.equal(ui.ids.ubicacionPedido.value, '');
});

test('respuesta vieja no reemplaza dirección modificada ni una búsqueda nueva', async () => {
    const ui = setup(); ui.ids.clienteDireccion.value = 'Primera'; ui.ids.buscarDireccion.fire('click');
    ui.ids.clienteDireccion.value = 'Segunda'; ui.ids.clienteDireccion.fire('input'); ui.ids.buscarDireccion.fire('click');
    await ui.reply(1, {resultados: [{...result, direccion:'Segunda'}]});
    await ui.reply(0, {resultados:[result]});
    assert.equal(ui.ids.resultadosDirecciones.children[0].textContent, 'Segunda');
});

test('distancia manual cancela ruta pendiente y no se sobrescribe con respuesta tardía', async () => {
    const ui = setup(); await choose(ui);
    ui.ids.distancia.value = '5.4'; ui.ids.distancia.fire('input');
    assert.equal(ui.calls[1].options.signal.aborted, true);
    await ui.reply(1, route); assert.equal(ui.ids.distancia.value, '5.4');
});

test('retirar, apagar o salir cancela consultas sin aplicar respuestas tardías', async () => {
    for (const action of ['pickup', 'off', 'leave']) {
        const ui = setup(); await choose(ui);
        if(action === 'pickup') ui.pickup();
        if(action === 'off') {ui.body.classList.add('system-off'); ui.observers[1]();}
        if(action === 'leave') ui.windowEvents.pagehide();
        await ui.reply(1, route); assert.equal(ui.ids.distancia.value, '');
    }
});

test('falta de clave y error de proveedor permiten distancia manual, no inventan kilómetros', async () => {
    const withoutKey = setup({enabled:false}); withoutKey.ids.buscarDireccion.fire('click'); assert.equal(withoutKey.calls.length, 0);
    const ui = setup(); await choose(ui); await ui.reply(1, {error:'Cuota agotada: ingresá kilómetros manualmente'}, false);
    assert.equal(ui.ids.distancia.value, ''); assert.match(ui.ids.estadoMapa.textContent, /Cuota/);
    ui.ids.distancia.value = '1.3'; ui.ids.distancia.fire('input'); assert.equal(ui.ids.distancia.value, '1.3');
});

test('recuperar ubicación no gasta créditos y un origen cambiado invalida la distancia', () => {
    const location = {...result, origen: [-27.455266,-58.992536], metros:1340, km:'1.3', geometria:geometry};
    const ui = setup({restored:JSON.stringify(location), address:result.direccion, distance:'1.3'});
    assert.equal(ui.calls.length, 0); assert.equal(ui.ids.detalleRecorrido.hidden, false);
    location.origen = [0,0];
    const changed = setup({restored:JSON.stringify(location), address:result.direccion, distance:'1.3'});
    assert.equal(changed.ids.distancia.value, ''); assert.equal(changed.ids.ubicacionPedido.value, '');
});

test('geometría malformada restaurada no rompe el formulario', () => {
    const ui = setup({restored:JSON.stringify({...result, origen:[-27.455266,-58.992536], geometria:{type:'MultiLineString', coordinates:'mal'}}), address:result.direccion});
    assert.equal(ui.ids.ubicacionPedido.value, ''); assert.equal(ui.calls.length, 0);
});

test('Enter busca sin enviar y enlaces Maps no disparan geocodificación', () => {
    const ui = setup(); let prevented = false;
    ui.ids.clienteDireccion.value = 'https://maps.google.com';
    ui.ids.clienteDireccion.fire('keydown', {key:'Enter',preventDefault() {prevented = true;}});
    assert.equal(prevented,true); assert.equal(ui.calls.length,0);
});
