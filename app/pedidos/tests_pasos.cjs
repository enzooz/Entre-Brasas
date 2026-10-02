/* Prueba el controlador real del flujo sin navegador ni base de producción. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/js/pasos-pedido.js'), 'utf8');

test('nombre y teléfono no heredan el margen vertical entre párrafos', () => {
    const css = fs.readFileSync(path.join(__dirname, '../static/css/sistema.css'), 'utf8');
    assert.match(css, /\.order-wizard \.client-fields > p\s*\{\s*margin:\s*0;\s*\}/);
});

function setup(step = '0') {
    const listeners = {}, rows = [];
    function node(id = '', value = '') {
        const classes = new Set();
        return {id, value, tagName: 'INPUT', type: 'text', hidden: false, textContent: '', children: [],
            valid: true, attrs: {}, listeners: {},
            classList: {add: x => classes.add(x), toggle: (x, on) => on ? classes.add(x) : classes.delete(x), contains: x => classes.has(x)},
            setAttribute(k, v) {this.attrs[k] = v;}, removeAttribute(k) {delete this.attrs[k];},
            addEventListener(k, fn) {this.listeners[k] = fn;}, focus() {this.focused = true;},
            checkValidity() {return this.valid;}, reportValidity() {this.reported = true;},
            appendChild(x) {this.children.push(x);}, replaceChildren() {this.children = [];}};
    }
    const ids = Object.fromEntries(['formPedido', 'pasoPedido', 'pasoAnterior', 'pasoSiguiente', 'crearPedido',
        'accionesPasos', 'estadoPaso', 'paso-resumen', 'clienteNombre', 'clienteTelefono', 'clienteDireccion',
        'distancia', 'sinProductos', 'resumenUnidades', 'reglaEnvio'].map(id => [id, node(id)]));
    ids.pasoPedido.value = step;
    const panels = Array.from({length: 4}, () => node()), steps = panels.map(() => node());
    const headings = panels.map(() => node());
    const delivery = node('', 'true');
    panels.forEach((panel, i) => {
        panel.querySelector = () => headings[i];
        panel.querySelectorAll = () => i === 0 ? [ids.clienteNombre, ids.clienteTelefono] : i === 3 ? [ids.clienteDireccion, ids.distancia] : [];
    });
    ids.formPedido.querySelectorAll = selector => selector === '.wizard-panel' ? panels : steps;
    ids.formPedido.querySelector = () => delivery;
    const document = {body: node(), getElementById: id => ids[id], querySelectorAll: () => rows,
        createElement: () => node(), addEventListener(k, fn) {(listeners[k] ||= []).push(fn);},
        dispatchEvent(event) {(listeners[event.type] || []).forEach(fn => fn(event));}};
    const Event = class {constructor(type) {this.type = type;}};
    vm.runInNewContext(source, {document, Event, DATOS: {costo_minimo_envio: 1000, distancia_minima: 1, tarifa_100m: 100}});
    document.dispatchEvent(new Event('DOMContentLoaded'));
    function submit() {const e = {preventDefault() {this.prevented = true;}}; ids.formPedido.listeners.submit(e); return e;}
    function unit(name, extras = [], note = '') {
        const item = {querySelector: s => ({textContent: name, value: note}),
            querySelectorAll: () => extras.map(x => ({type: 'checkbox', closest: () => ({textContent: x})}))};
        rows.push(item); document.dispatchEvent(new Event('pedido:actualizado')); return item;
    }
    return {ids, panels, headings, steps, delivery, rows, document, Event, submit, unit};
}

test('muestra un solo paso y bloquea avanzar si falta cliente o hamburguesa', () => {
    const ui = setup();
    assert.equal(ui.panels.filter(x => !x.hidden).length, 1);
    assert.equal(ui.ids.crearPedido.hidden, true);
    assert.equal(ui.ids.pasoAnterior.disabled, true);
    ui.steps[3].listeners.click();
    assert.equal(ui.ids.pasoPedido.value, '0');
    assert.equal(ui.ids.clienteNombre.focused, true);
    ui.ids.clienteNombre.value = 'Cliente de prueba';
    ui.ids.pasoSiguiente.listeners.click();
    assert.equal(ui.ids.pasoPedido.value, '1');
    ui.ids.pasoSiguiente.listeners.click();
    assert.equal(ui.ids.pasoPedido.value, '1');
    assert.equal(ui.ids.sinProductos.focused, true);
});

test('Cliente usa altura natural y los demás pasos recuperan el panel desplazable', () => {
    const ui = setup();
    assert.equal(ui.document.body.classList.contains('order-client-step'), true);
    ui.ids.clienteNombre.value = 'Prueba';
    ui.ids.pasoSiguiente.listeners.click();
    assert.equal(ui.document.body.classList.contains('order-client-step'), false);
    ui.ids.pasoAnterior.listeners.click();
    assert.equal(ui.document.body.classList.contains('order-client-step'), true);
    assert.equal(ui.ids.clienteNombre.value, 'Prueba');
    assert.equal(setup('2').document.body.classList.contains('order-client-step'), false);
});

test('avanza, retrocede sin borrar y confirma exclusivamente al final', () => {
    const ui = setup(); ui.ids.clienteNombre.value = 'Prueba'; ui.unit('Baconera');
    assert.equal(ui.submit().prevented, true);
    assert.equal(ui.ids.pasoPedido.value, '3');
    assert.equal(ui.ids.crearPedido.hidden, false);
    assert.equal(ui.submit().prevented, undefined);
    ui.ids.pasoAnterior.listeners.click();
    assert.equal(ui.ids.pasoPedido.value, '2');
    assert.equal(ui.ids.clienteNombre.value, 'Prueba');
    assert.equal(ui.rows.length, 1);
});

test('error en un panel oculto lo muestra y enfoca el campo concreto', () => {
    const ui = setup('3'); ui.ids.clienteNombre.value = 'Prueba'; ui.unit('Cheese');
    ui.ids.distancia.valid = false;
    assert.equal(ui.submit().prevented, true);
    assert.equal(ui.ids.pasoPedido.value, '3');
    assert.equal(ui.ids.distancia.focused, true);
    ui.ids.distancia.valid = true; ui.delivery.value = 'false';
    ui.ids.clienteDireccion.value = 'Dirección de prueba';
    assert.equal(ui.submit().prevented, true);
    assert.equal(ui.ids.pasoPedido.value, '0');
    assert.equal(ui.ids.clienteTelefono.focused, true);
    ui.ids.clienteTelefono.value = '12345678';
    ui.steps[3].listeners.click();
    assert.equal(ui.submit().prevented, undefined);
});

test('borrador recupera el paso, descartar vuelve a Cliente y Enter no crea pedidos', () => {
    const ui = setup('2');
    assert.equal(ui.panels[2].hidden, false);
    ui.document.dispatchEvent(new ui.Event('pedido:borrador-descartado'));
    assert.equal(ui.ids.pasoPedido.value, '0');
    ui.ids.clienteNombre.value = 'Prueba';
    const e = {key: 'Enter', target: ui.ids.clienteNombre, preventDefault() {this.prevented = true;}};
    ui.ids.formPedido.listeners.keydown(e);
    assert.equal(e.prevented, true);
    assert.equal(ui.ids.pasoPedido.value, '1');
    assert.equal(ui.ids.crearPedido.hidden, true);
    assert.equal(setup('corrupto').ids.pasoPedido.value, '0');
});

test('resumen mantiene los extras y notas separados por unidad, como texto seguro', () => {
    const ui = setup();
    ui.unit('Baconera', ['Panceta'], 'Sin cebolla'); ui.unit('Baconera', [], '<b>Bien cocida</b>');
    assert.equal(ui.ids.resumenUnidades.children[0].textContent, '1. Baconera · Panceta · Nota: Sin cebolla');
    assert.equal(ui.ids.resumenUnidades.children[1].textContent, '2. Baconera · Nota: <b>Bien cocida</b>');
    assert.match(ui.ids.reglaEnvio.textContent, /1000 hasta 1 km/);
});
