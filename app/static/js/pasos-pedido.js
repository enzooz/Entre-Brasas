/* Una sección visible; el pedido solo se guarda al confirmar el cuarto paso. */
document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('formPedido');
    if (!form) return;
    var panels = Array.from(form.querySelectorAll('.wizard-panel'));
    var steps = Array.from(form.querySelectorAll('.order-steps button'));
    var saved = document.getElementById('pasoPedido');
    var previous = document.getElementById('pasoAnterior');
    var next = document.getElementById('pasoSiguiente');
    var create = document.getElementById('crearPedido');
    var actions = document.getElementById('accionesPasos');
    var status = document.getElementById('estadoPaso');
    var summary = document.getElementById('paso-resumen');
    var current = 0;
    var names = ['Cliente', 'Hamburguesas', 'Pago', 'Ubicación'];
    form.classList.add('order-wizard');
    document.body.classList.add('order-entry');
    form.noValidate = true; // Validamos antes de ocultar/mover el foco al campo.
    actions.hidden = false;
    actions.appendChild(create);

    function show(index, focus, persist) {
        current = index;
        document.body.classList.toggle('order-client-step', index === 0);
        saved.value = String(index);
        panels.forEach(function (panel, i) { panel.hidden = i !== index; });
        steps.forEach(function (button, i) {
            if (i === index) button.setAttribute('aria-current', 'step');
            else button.removeAttribute('aria-current');
        });
        previous.disabled = index === 0;
        next.hidden = index === 3;
        create.hidden = index !== 3;
        status.textContent = 'Paso ' + (index + 1) + ' de 4 · ' + names[index];
        next.textContent = 'Continuar: ' + names[Math.min(index + 1, 3)];
        summary.classList.toggle('is-final', index === 3);
        if (focus) panels[index].querySelector('h2').focus({preventScroll: true});
        if (persist !== false) document.dispatchEvent(new Event('pedido:actualizado'));
    }

    function invalid(index, field, message) {
        show(index, false);
        status.textContent = message || 'Revisá el campo marcado para continuar.';
        field.focus();
        if (field.reportValidity) field.reportValidity();
        return false;
    }

    function validate(index) {
        var fields = Array.from(panels[index].querySelectorAll('input, textarea, select'));
        for (var field of fields) {
            // Teléfono se completa en Cliente; su obligatoriedad depende del último paso.
            if (index === 0 && field.id === 'clienteTelefono' && !field.value.trim()) continue;
            if (!field.checkValidity()) return invalid(index, field);
        }
        if (index === 0) {
            var name = document.getElementById('clienteNombre');
            if (!name.value.trim()) return invalid(0, name, 'Ingresá el nombre del cliente.');
            var phone = document.getElementById('clienteTelefono');
            if (phone.value.trim() && (!/^[0-9+\s().-]+$/.test(phone.value) || !/^[0-9]{7,20}$/.test(phone.value.replace(/[^0-9]/g, '')))) {
                return invalid(0, phone, 'El teléfono debe tener entre 7 y 20 dígitos.');
            }
        }
        if (index === 1 && !document.querySelectorAll('.fila-producto').length) {
            return invalid(1, document.getElementById('sinProductos'), 'Agregá al menos una hamburguesa para continuar.');
        }
        if (index === 3) {
            var delivery = form.querySelector('input[name="retiro_local"]:checked');
            if (delivery && delivery.value === 'false') {
                var phone = document.getElementById('clienteTelefono');
                if (!phone.value.trim()) return invalid(0, phone, 'Para envío también necesitamos el teléfono.');
                var address = document.getElementById('clienteDireccion');
                if (!address.value.trim()) return invalid(3, address, 'Ingresá la dirección del envío.');
            }
        }
        return true;
    }

    function go(index) {
        if (index > current) {
            for (var i = 0; i < index; i++) if (!validate(i)) return;
        }
        show(index, true);
    }
    steps.forEach(function (button, i) { button.addEventListener('click', function () { go(i); }); });
    previous.addEventListener('click', function () { go(Math.max(0, current - 1)); });
    next.addEventListener('click', function () { go(Math.min(3, current + 1)); });
    form.addEventListener('keydown', function (event) {
        if (event.key !== 'Enter' || event.target.tagName !== 'INPUT' || event.target.type === 'search') return;
        event.preventDefault(); // Enter nunca crea un pedido ni elige extras por accidente.
        if (!['checkbox', 'radio'].includes(event.target.type) && current < 3) go(current + 1);
    });
    form.addEventListener('submit', function (event) {
        for (var i = 0; i < 4; i++) {
            if (!validate(i)) { event.preventDefault(); return; }
        }
        if (current !== 3) { event.preventDefault(); show(3, true); }
    });
    document.addEventListener('pedido:borrador-descartado', function () { show(0, true, false); });

    function renderUnits() {
        var list = document.getElementById('resumenUnidades');
        list.replaceChildren();
        document.querySelectorAll('.fila-producto').forEach(function (row, i) {
            var item = document.createElement('li');
            var text = (i + 1) + '. ' + row.querySelector('.fila-nombre').textContent;
            row.querySelectorAll('.chips-adicionales input:checked, .selector-medallones input:checked').forEach(function (input) {
                if (input.type === 'radio' && input.value === '0') return;
                text += ' · ' + input.closest('label').textContent.trim();
            });
            var note = row.querySelector('.campo-nota').value.trim();
            item.textContent = text + (note ? ' · Nota: ' + note : '');
            list.appendChild(item);
        });
    }
    document.addEventListener('pedido:actualizado', renderUnits);
    form.addEventListener('input', renderUnits);
    document.getElementById('reglaEnvio').textContent = 'Envío mínimo $' + DATOS.costo_minimo_envio + ' hasta ' + String(DATOS.distancia_minima).replace('.', ',') + ' km. Después, $' + DATOS.tarifa_100m + ' por cada 100 metros excedentes.';
    var restored = Number(saved.value);
    show(Number.isInteger(restored) && restored >= 0 && restored <= 3 ? restored : 0, false, false);
    renderUnits();
});
