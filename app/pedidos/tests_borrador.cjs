const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/js/borrador-pedido.js'), 'utf8');
const key = 'entre-brasas-pedido-borrador-v1';
const token = '75c33a01-fb02-4c8f-8103-ffea8f13be01';

function setup({storage = new Map(), cookie = '', formPresent = true, failStorage = false, prices = 13500, available = true} = {}) {
    function node(value = '') {
        const classes = new Set();
        return {value, hidden: true, checked: false, open: false, textContent: '', listeners: {},
            classList: {add: x => classes.add(x), remove: x => classes.delete(x), contains: x => classes.has(x), toggle: (x, on) => on ? classes.add(x) : classes.delete(x)},
            addEventListener(type, fn) { this.listeners[type] = fn; }, focus() { this.focused = true; }};
    }
    const ids = Object.fromEntries(['clienteNombre', 'observaciones', 'clienteDireccion', 'clienteTelefono', 'distancia', 'mensajeWhatsapp',
        'clienteGuardadoId', 'borradorAviso', 'borradorEstado', 'borradorAyuda', 'borradorToken', 'descartarBorrador', 'resultadoMensaje', 'listaProductos'].map(id => [id, node()]));
    const rows = [], details = node(), events = {}, windowEvents = {};
    const delivery = [node('true'), node('false')], payment = [node('efectivo'), node('transferencia')];
    payment[0].checked = true;
    const form = node();
    form.querySelectorAll = selector => selector.includes('retiro_local') ? delivery : payment;
    form.querySelector = selector => form.querySelectorAll(selector).find(x => x.checked) || null;
    form.reset = () => { ['clienteGuardadoId', 'clienteNombre', 'observaciones', 'clienteDireccion', 'clienteTelefono', 'distancia', 'mensajeWhatsapp'].forEach(id => ids[id].value = ''); delivery.forEach(x => x.checked = false); payment[0].checked = true; payment[1].checked = false; };
    Object.defineProperty(ids.listaProductos, 'innerHTML', {set() { rows.length = 0; }});
    function createRow(id) {
        const note = node(), meats = [node('0'), node('1'), node('2')], extras = [node('10'), node('11')], meatGroup = node();
        meatGroup.hidden = false;
        meats[0].checked = true;
        meats.forEach(input => { let marked = input.checked; Object.defineProperty(input, 'checked', {get: () => marked, set(value) { if (value) meats.filter(x => x !== input).forEach(x => x.checked = false); marked = value; }}); });
        const row = {dataset: {hamburguesa: String(id), precio: String(prices)}, note, meats, extras,
            querySelector(selector) { if (selector === '.campo-nota') return note; if (selector === '.selector-medallones') return meatGroup; return meats.find(x => x.checked); },
            querySelectorAll(selector) { const inputs = selector.includes('chips') ? extras : meats; return selector.includes(':checked') ? inputs.filter(x => x.checked) : inputs; }};
        rows.push(row); return row;
    }
    const buttons = available ? [{dataset: {id: '1', nombre: 'Baconera', precio: String(prices)}}] : [];
    const document = {cookie, hidden: false, getElementById: id => id === 'formPedido' ? (formPresent ? form : null) : ids[id],
        querySelector: () => details, querySelectorAll: selector => selector === '.boton-menu' ? buttons : rows,
        addEventListener(type, fn) { events[type] = fn; }};
    const window = {crypto: {randomUUID: () => token}, confirm: () => true,
        sessionStorage: {getItem: k => storage.get(k) || null, setItem(k, v) { if (failStorage) throw new Error('No permite'); storage.set(k, v); }, removeItem: k => storage.delete(k)},
        addEventListener(type, fn) { windowEvents[type] = fn; }};
    vm.runInNewContext(source, {window, document, crearFila: createRow, cambiarEntrega() {}, mostrarLinkMaps() {}, calcularTotal() {}});
    events.DOMContentLoaded();
    return {storage, ids, form, rows, createRow, delivery, payment, details, document, events, windowEvents};
}

test('guarda y recupera campos, unidades independientes, extras, medallones y notas', () => {
    const ui = setup();
    ui.ids.clienteNombre.value = 'Prueba de borrador';
    ui.ids.clienteGuardadoId.value = '7';
    ui.ids.clienteDireccion.value = 'Dirección de prueba';
    ui.ids.clienteTelefono.value = '123';
    ui.ids.distancia.value = '5.4';
    ui.ids.observaciones.value = 'Tocar timbre';
    ui.ids.mensajeWhatsapp.value = 'Mensaje sin interpretar';
    ui.details.open = true;
    ui.delivery[1].checked = true;
    ui.payment[0].checked = false; ui.payment[1].checked = true;
    const first = ui.createRow(1), second = ui.createRow(1);
    first.note.value = 'Sin cebolla'; first.extras[0].checked = true; first.meats[1].checked = true;
    second.note.value = 'Bien cocida';
    ui.form.listeners.input();
    const saved = JSON.parse(ui.storage.get(key));
    assert.equal(saved.items.length, 2);
    assert.equal(saved.fields.clienteGuardadoId, '7');
    assert.deepEqual(saved.items[0].extras, ['10']);
    assert.deepEqual(saved.items[1].extras, []);
    assert.equal(JSON.stringify(saved).includes('csrf'), false);
    assert.equal(JSON.stringify(saved).includes('precio'), false);
    const next = setup({storage: ui.storage, prices: 14000});
    assert.equal(next.ids.clienteNombre.value, 'Prueba de borrador');
    assert.equal(next.ids.distancia.value, '5.4');
    assert.equal(next.rows[0].note.value, 'Sin cebolla');
    assert.equal(next.rows[1].note.value, 'Bien cocida');
    assert.equal(next.rows[0].extras[0].checked, true);
    assert.equal(next.rows[1].extras[0].checked, false);
    assert.equal(next.rows[0].meats[1].checked, true);
    assert.equal(next.rows[0].dataset.precio, '14000');
    assert.equal(next.payment[1].checked, true);
    assert.equal(next.ids.borradorEstado.textContent, 'Retomaste tu pedido a medio cargar');
});

test('salir o enviar guarda el borrador, sin asumir que el pedido se creó', () => {
    const ui = setup(); ui.ids.clienteNombre.value = 'Pendiente';
    ui.windowEvents.pagehide();
    assert.ok(ui.storage.has(key));
    ui.form.listeners.submit();
    assert.ok(ui.storage.has(key));
});

test('confirmación del servidor limpia solo el borrador de esta pestaña', () => {
    const ui = setup(); ui.ids.clienteNombre.value = 'Creado'; ui.form.listeners.input();
    setup({storage: ui.storage, formPresent: false, cookie: 'eb_pedido_creado_' + token.replaceAll('-', '') + '=1'});
    assert.equal(ui.storage.has(key), false);
});

test('la confirmación de otro pedido no borra el borrador actual', () => {
    const ui = setup(); ui.ids.clienteNombre.value = 'Otro'; ui.form.listeners.input();
    setup({storage: ui.storage, formPresent: false, cookie: 'eb_pedido_creado_otra_pestana=1'});
    assert.equal(ui.storage.has(key), true);
});

test('el descarte explícito vacía los campos y el almacenamiento', () => {
    const ui = setup(); ui.ids.clienteNombre.value = 'A descartar'; ui.createRow(1); ui.form.listeners.input();
    ui.ids.descartarBorrador.listeners.click();
    assert.equal(ui.storage.has(key), false);
    assert.equal(ui.ids.clienteNombre.value, '');
    assert.equal(ui.rows.length, 0);
});

test('volver atrás después de crear no resucita el pedido enviado', () => {
    const ui = setup(); ui.ids.clienteNombre.value = 'Ya creado'; ui.form.listeners.input();
    ui.storage.delete(key); ui.windowEvents.pageshow({persisted: true});
    assert.equal(ui.ids.clienteNombre.value, '');
});

test('datos ilegibles se avisan y no se borran al salir', () => {
    const storage = new Map([[key, '{incompleto']]);
    const ui = setup({storage}); ui.windowEvents.pagehide();
    assert.equal(storage.get(key), '{incompleto');
    assert.match(ui.ids.borradorEstado.textContent, /No se pudo recuperar/);
});

test('si el navegador rechaza guardar no se muestra una confirmación falsa', () => {
    const ui = setup({failStorage: true}); ui.ids.clienteNombre.value = 'No guardado'; ui.form.listeners.input();
    assert.match(ui.ids.borradorEstado.textContent, /No se pudo guardar/);
    assert.equal(ui.storage.has(key), false);
});

test('los productos que ya no se ofrecen se avisan al recuperar', () => {
    const ui = setup(); ui.createRow(1); ui.form.listeners.input();
    const next = setup({storage: ui.storage, available: false});
    assert.match(next.ids.borradorAyuda.textContent, /ya no están disponibles/);
    assert.equal(next.ids.borradorAviso.classList.contains('is-warning'), true);
});
