const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/js/clientes-pedido.js'), 'utf8');

function setup(fetchImpl = async () => ({ok:true, json:async () => ({clientes:[]})})) {
    function node() { return {value:'', textContent:'', hidden:false, children:[], listeners:{}, dataset:{url:'/pedidos/clientes/buscar/'},
        addEventListener(type, fn) { this.listeners[type]=fn; }, replaceChildren() { this.children=[]; },
        append(...children) { this.children.push(...children); }, appendChild(child) { this.children.push(child); }, focus() { this.focused=true; }}; }
    const ids = Object.fromEntries(['buscarCliente','estadoClientes','resultadosClientes','clienteGuardadoId','clienteNombre','clienteTelefono','clienteDireccion','distancia','botonBuscarCliente','clienteNuevo','formPedido'].map(id => [id,node()]));
    const events = {}, timers = new Map(), calls = [];
    let updated=0;
    vm.runInNewContext(source, {
        document: {getElementById:id => ids[id], createElement:node, addEventListener(type, fn) { events[type]=fn; }},
        window: {setTimeout(fn,delay) { const key=Symbol(); timers.set(key,{fn,delay}); return key; }, clearTimeout(key) { timers.delete(key); }},
        AbortController, encodeURIComponent,
        fetch(...args) { calls.push(args); return fetchImpl(...args); }, mostrarLinkMaps() {}, calcularTotal() { updated++; },
    });
    events.DOMContentLoaded();
    return {ids,events,timers,calls,updated:() => updated, lookup:() => ids.botonBuscarCliente.listeners.click()};
}
const customer = {id:7, nombre:'Cliente de prueba', telefono:'3621234567', direccion:'Dirección de prueba'};

test('elige un resultado sin guardar, cambia solo datos del cliente y actualiza el borrador', async () => {
    const ui=setup(async () => ({ok:true,json:async () => ({clientes:[customer]})}));
    ui.ids.buscarCliente.value='Cliente';
    await ui.lookup();
    assert.equal(ui.ids.resultadosClientes.hidden,false);
    assert.equal(ui.ids.clienteNombre.value,'');
    ui.ids.distancia.value='5.4';
    ui.ids.resultadosClientes.children[0].listeners.click();
    assert.equal(ui.ids.clienteGuardadoId.value,'7');
    assert.equal(ui.ids.clienteNombre.value,customer.nombre);
    assert.equal(ui.ids.clienteTelefono.value,customer.telefono);
    assert.equal(ui.ids.clienteDireccion.value,customer.direccion);
    assert.equal(ui.ids.distancia.value,'');
    assert.equal(ui.updated(),1);
    assert.equal(ui.calls[0][1].cache,'no-store');
});
test('nuevo cliente limpia datos sin enviar pedidos', () => {
    const ui=setup();
    ui.ids.clienteGuardadoId.value='7'; ui.ids.clienteNombre.value='Anterior';
    ui.ids.clienteNuevo.listeners.click();
    assert.equal(ui.ids.clienteGuardadoId.value,''); assert.equal(ui.ids.clienteNombre.value,'');
    assert.equal(ui.calls.length,0); assert.equal(ui.updated(),1);
});
test('consulta corta no hace peticiones; Enter busca sin enviar el formulario', async () => {
    const ui=setup(); ui.ids.buscarCliente.value='a'; await ui.lookup();
    assert.equal(ui.calls.length,0);
    let prevented=false; ui.ids.buscarCliente.value='Cliente';
    ui.ids.buscarCliente.listeners.keydown({key:'Enter',preventDefault() { prevented=true; }});
    assert.equal(prevented,true); assert.equal(ui.calls.length,1);
});
test('vacío y error permiten continuar manualmente', async () => {
    const empty=setup(); empty.ids.buscarCliente.value='No existe'; await empty.lookup();
    assert.match(empty.ids.estadoClientes.textContent,/No encontramos/);
    const bad=setup(async () => { throw new Error('Sin conexión'); }); bad.ids.buscarCliente.value='Cliente'; await bad.lookup();
    assert.match(bad.ids.estadoClientes.textContent,/reintentar/);
});
test('respuesta vieja no reemplaza una búsqueda más reciente', async () => {
    let resolve;
    const ui=setup(() => new Promise(done => { resolve=done; })); ui.ids.buscarCliente.value='Antes';
    const pending=ui.lookup();
    ui.ids.buscarCliente.value='Después'; ui.ids.buscarCliente.listeners.input();
    resolve({ok:true,json:async () => ({clientes:[customer]})}); await pending;
    assert.equal(ui.ids.resultadosClientes.children.length,0);
});
test('nombres y direcciones se insertan como texto, no como HTML', async () => {
    const ui=setup(async () => ({ok:true,json:async () => ({clientes:[{...customer,nombre:'<img onerror=alert(1)>',direccion:'<script>error</script>'}]})}));
    ui.ids.buscarCliente.value='Cliente'; await ui.lookup();
    const result=ui.ids.resultadosClientes.children[0];
    assert.equal(result.children[0].textContent,'<img onerror=alert(1)>');
    assert.equal(result.innerHTML,undefined);
});
test('editar nombre o teléfono anula la selección y Escape cierra resultados', () => {
    const ui=setup(); ui.ids.clienteGuardadoId.value='7'; ui.ids.clienteNombre.listeners.input();
    assert.equal(ui.ids.clienteGuardadoId.value,'');
    ui.ids.buscarCliente.listeners.keydown({key:'Escape'}); assert.equal(ui.ids.resultadosClientes.hidden,true);
});
