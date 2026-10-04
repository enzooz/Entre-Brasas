/* Pruebas unitarias del comportamiento compartido, sin base ni navegador real. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/js/estado-sistema.js'), 'utf8');

function setup({off = false, marker = null, state = {instancia: 'actual', apagando: false}} = {}) {
    function element() {
        return {hidden: true, inert: false, disabled: false, textContent: '',
            listeners: {}, setAttribute() {}, focus() { this.focused = true; },
            addEventListener(type, fn) { this.listeners[type] = fn; }};
    }
    const ids = Object.fromEntries(['system-off-notice', 'system-off-title', 'system-off-message', 'system-reconnect'].map(id => [id, element()]));
    const selectors = Object.fromEntries(['.nav-scrim', '.menu-toggle', '.sidebar', '.app-main', '.skip-link'].map(id => [id, element()]));
    const control = element();
    const classes = new Set();
    const body = {dataset: {systemInstance: 'actual', systemStatusUrl: '/sistema/estado/', systemOff: off ? 'true' : undefined},
        classList: {add: x => classes.add(x), remove: x => classes.delete(x)}};
    ids['system-off-notice'].contains = target => target === ids['system-reconnect'];
    const events = {}, windowEvents = {};
    const saved = new Map(marker ? [['entre-brasas-apagado', marker]] : []);
    let interval, fetchState = state, assigned;
    const document = {body, hidden: false, getElementById: id => ids[id],
        querySelector: selector => selectors[selector], querySelectorAll: () => [control],
        addEventListener(type, fn) { events[type] = fn; }};
    const window = {localStorage: {getItem: key => saved.get(key), setItem: (key, value) => saved.set(key, value)},
        location: {assign: url => { assigned = url; }},
        addEventListener(type, fn) { windowEvents[type] = fn; },
        setTimeout() { return 1; }, clearTimeout() {}, setInterval(fn) { interval = fn; }};
    const fetch = async () => {
        if (fetchState instanceof Error) throw fetchState;
        return {ok: true, json: async () => fetchState};
    };
    vm.runInNewContext(source, {document, window, fetch, AbortController});
    events.DOMContentLoaded();
    return {ids, selectors, control, classes, saved, events, windowEvents,
        assigned: () => assigned, setState: value => { fetchState = value; },
        tick: async () => { await new Promise(resolve => setImmediate(resolve)); await interval(); }};
}

test('activo: no bloquea la pantalla ni reutiliza un apagado de otra ejecución', async () => {
    const ui = setup({marker: 'ejecucion-anterior'});
    await ui.tick();
    assert.equal(ui.classes.has('system-off'), false);
    assert.equal(ui.control.disabled, false);
    assert.equal(ui.ids['system-off-notice'].hidden, true);
});

test('apagado: todas las áreas y campos quedan inactivos, con aviso y foco', async () => {
    const ui = setup({state: {instancia: 'actual', apagando: true}});
    await ui.tick();
    assert.equal(ui.classes.has('system-off'), true);
    assert.equal(ui.selectors['.sidebar'].inert, true);
    assert.equal(ui.selectors['.app-main'].inert, true);
    assert.equal(ui.control.disabled, true);
    assert.equal(ui.ids['system-off-notice'].hidden, false);
    assert.equal(ui.ids['system-off-notice'].focused, true);
    assert.equal(ui.ids['system-off-title'].textContent, 'Sistema apagado');
    assert.equal(ui.saved.get('entre-brasas-apagado'), 'actual');
});

test('las otras pestañas se bloquean al recibir el aviso de apagado', async () => {
    const ui = setup();
    await ui.tick();
    ui.windowEvents.storage({key: 'entre-brasas-apagado', newValue: 'actual'});
    assert.equal(ui.classes.has('system-off'), true);
    assert.equal(ui.ids['system-off-title'].textContent, 'Sistema apagado');
    assert.equal(ui.ids['system-reconnect'].disabled, true);
});

test('una respuesta activa vieja no habilita volver mientras se está apagando', async () => {
    const ui = setup();
    await ui.tick();
    ui.windowEvents.storage({key: 'entre-brasas-apagado', newValue: 'actual'});
    await ui.tick();
    assert.equal(ui.ids['system-reconnect'].disabled, true);
});

test('el bloqueo detiene clicks, teclado y envío incluso sin soporte de inert', async () => {
    const ui = setup({off: true});
    await ui.tick();
    for (const type of ['click', 'submit', 'keydown', 'beforeinput', 'change']) {
        let prevented = false, stopped = false;
        ui.events[type]({target: ui.control, preventDefault() { prevented = true; }, stopImmediatePropagation() { stopped = true; }});
        assert.equal(prevented && stopped, true, type);
    }
});

test('un chequeo lento o fallido suelto no bloquea (por ejemplo, mientras carga el mapa)', async () => {
    const ui = setup({state: new Error('Tardó demasiado')});
    await ui.tick();  // Chequeo inicial + uno del intervalo: 2 fallas seguidas.
    await ui.tick();  // 3 fallas: todavia no bloquea.
    assert.equal(ui.classes.has('system-off'), false);
    ui.setState({instancia: 'actual', apagando: false});
    await ui.tick();  // Responde: se reinicia la cuenta.
    ui.setState(new Error('Tardó demasiado'));
    await ui.tick();
    await ui.tick();
    await ui.tick();
    assert.equal(ui.classes.has('system-off'), false);
    assert.equal(ui.ids['system-off-notice'].hidden, true);
});

test('una conexión perdida bloquea sin afirmar un apagado confirmado', async () => {
    const ui = setup({state: new Error('No conecta')});
    await ui.tick();
    await ui.tick();
    await ui.tick();  // Recién con 4 fallas seguidas se bloquea.
    assert.equal(ui.classes.has('system-off'), true);
    assert.equal(ui.ids['system-off-title'].textContent, 'Sistema sin conexión');
    assert.equal(ui.ids['system-reconnect'].disabled, true);
});

test('reabrir ofrece recargar, sin habilitar ni enviar borradores automáticamente', async () => {
    const ui = setup({off: true, state: new Error('Apagado')});
    await ui.tick();
    ui.setState({instancia: 'nueva', apagando: false});
    await ui.tick();
    assert.equal(ui.control.disabled, true);
    assert.equal(ui.classes.has('system-off'), true);
    assert.equal(ui.ids['system-reconnect'].disabled, false);
    assert.match(ui.ids['system-off-message'].textContent, /cambios sin guardar no se enviaron/);
    assert.equal(ui.assigned(), undefined);
    ui.ids['system-reconnect'].listeners.click();
    assert.equal(ui.assigned(), '/');
});
