/* Verifica el cálculo real que usa el resumen del formulario. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const template = fs.readFileSync(path.join(__dirname, '../templates/pedidos/crear_pedido.html'), 'utf8');
const start = template.indexOf('// El envio se calcula');
const end = template.indexOf("document.getElementById('totalHamburguesas')", start);
assert.ok(start >= 0 && end > start, 'El bloque de cálculo debe estar presente');
const source = template.slice(start, end);

test('el resumen cobra el mínimo y solamente la distancia excedente; retiro gratis', () => {
    for (const [distance, retiro, expected] of [
        ['0.1', false, 1000], ['0.9', false, 1000], ['1', false, 1000], ['5.4', false, 3200],
        ['', false, 0], ['-1', false, 0], ['999.91', false, 0],
        ['5.45', false, 0], ['5.4', true, 0],
    ]) {
        const context = {DATOS: {distancia_minima: 1, costo_minimo_envio: 1000, tarifa_100m: '50.00'},
            document: {querySelector: () => ({value: String(retiro)}), getElementById: () => ({value: distance})}};
        vm.runInNewContext(source, context);
        assert.equal(context.costoEnvio, expected, `${distance} km, retiro ${retiro}`);
    }
});

test('ejemplo solicitado y otra configuración sin constantes escondidas', () => {
    for (const [base, included, rate, distance, expected] of [
        [1000, 1, 100, '0', 1000], [1000, 1, 100, '0.1', 1000],
        [1000, 1, 100, '1', 1000], [1000, 1, 100, '1.1', 1100],
        [1000, 1, 100, '1.3', 1300], [1000, 1, 100, '5,4', 5400],
        [700, 2.3, 80, '2.3', 700], [700, 2.3, 80, '2.7', 1020],
    ]) {
        const context = {DATOS: {distancia_minima: included, costo_minimo_envio: base, tarifa_100m: rate},
            document: {querySelector: () => ({value: 'false'}), getElementById: () => ({value: distance})}};
        vm.runInNewContext(source, context);
        assert.equal(context.costoEnvio, expected);
    }
});

test('el resumen redondea el total monetario una sola vez', () => {
    const context = {DATOS: {distancia_minima: 0, costo_minimo_envio: 1000, tarifa_100m: '55.05'},
        document: {querySelector: () => ({value: 'false'}), getElementById: () => ({value: '1'})}};
    vm.runInNewContext(source, context);
    assert.equal(context.costoEnvio, 1551);
});
