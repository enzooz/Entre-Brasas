/* Borrador local por pestaña: no envía datos ni crea pedidos automáticamente. */
document.addEventListener('DOMContentLoaded', function () {
    var key = 'entre-brasas-pedido-borrador-v1';
    var form = document.getElementById('formPedido');
    var draft = null;
    var storageProblem = false;
    var uuidPattern = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/;
    try {
        var raw = window.sessionStorage.getItem(key);
        if (raw) {
            draft = JSON.parse(raw);
            if (draft.version !== 1 || !uuidPattern.test(draft.token) || !Array.isArray(draft.items)
                || !draft.fields || typeof draft.fields !== 'object' || Array.isArray(draft.fields)) throw new Error('Borrador inválido');
            var cookie = 'eb_pedido_creado_' + draft.token.replace(/-/g, '');
            if (document.cookie.split(';').some(function (value) { return value.trim() === cookie + '=1'; })) {
                window.sessionStorage.removeItem(key);
                document.cookie = cookie + '=; Max-Age=0; Path=/; SameSite=Strict';
                draft = null;
            }
        }
    } catch (error) { storageProblem = true; }
    // La confirmación también se procesa en el detalle, sin esperar al próximo pedido.
    if (!form) return;

    var fieldIds = ['clienteNombre', 'observaciones', 'clienteDireccion', 'clienteTelefono', 'distancia', 'mensajeWhatsapp'];
    var notice = document.getElementById('borradorAviso');
    var state = document.getElementById('borradorEstado');
    var help = document.getElementById('borradorAyuda');
    var restoring = false;
    var token = draft ? draft.token : window.crypto.randomUUID();
    document.getElementById('borradorToken').value = token;

    function show(text, warning) {
        notice.hidden = false;
        notice.classList.toggle('is-warning', !!warning);
        if (state.textContent !== text) state.textContent = text;
    }

    function selected(name) {
        var input = form.querySelector('input[name="' + name + '"]:checked');
        return input ? input.value : null;
    }

    function capture() {
        var fields = {};
        fieldIds.forEach(function (id) { fields[id] = document.getElementById(id).value; });
        return {
            version: 1, token: token, fields: fields,
            entrega: selected('retiro_local'), pago: selected('metodo_pago'),
            mensajeAbierto: document.querySelector('.card-pegar').open,
            items: Array.from(document.querySelectorAll('.fila-producto')).map(function (row) {
                var extraMeat = row.querySelector('.selector-medallones input:checked');
                return {
                    hamburguesa: Number(row.dataset.hamburguesa),
                    nota: row.querySelector('.campo-nota').value,
                    medallones: extraMeat ? extraMeat.value : '0',
                    extras: Array.from(row.querySelectorAll('.chips-adicionales input:checked')).map(function (input) { return input.value; }),
                };
            }),
        };
    }

    function meaningful(data) {
        return data.items.length || data.entrega || data.pago !== 'efectivo'
            || fieldIds.some(function (id) { return data.fields[id].trim(); });
    }

    function save() {
        if (restoring) return;
        try {
            var data = capture();
            if (!meaningful(data)) {
                if (storageProblem) return; // No borrar contenido ilegible al salir de una pantalla vacía.
                window.sessionStorage.removeItem(key);
                notice.hidden = true;
                return;
            }
            window.sessionStorage.setItem(key, JSON.stringify(data));
            if (!notice.classList.contains('is-warning')) show('Borrador guardado en esta pestaña');
        } catch (error) {
            show('No se pudo guardar el borrador en este navegador', true);
            help.textContent = 'No salgas de esta pantalla hasta crear el pedido: el navegador no permite guardar el borrador.';
        }
    }

    function restore(data) {
        restoring = true;
        var unavailable = data.items.length > 100;
        fieldIds.forEach(function (id) {
            if (typeof data.fields[id] === 'string') document.getElementById(id).value = data.fields[id];
        });
        form.querySelectorAll('input[name="retiro_local"]').forEach(function (input) { input.checked = input.value === data.entrega; });
        form.querySelectorAll('input[name="metodo_pago"]').forEach(function (input) { input.checked = input.value === data.pago; });
        document.querySelector('.card-pegar').open = !!data.mensajeAbierto;
        document.getElementById('listaProductos').innerHTML = '';
        var buttons = Array.from(document.querySelectorAll('.boton-menu'));
        data.items.slice(0, 100).forEach(function (item) {
            if (!item || !Number.isInteger(item.hamburguesa)) { unavailable = true; return; }
            var button = buttons.find(function (candidate) { return Number(candidate.dataset.id) === item.hamburguesa; });
            if (!button) { unavailable = true; return; }
            // Los precios y extras se toman del menú actual, nunca del borrador.
            var row = crearFila(item.hamburguesa, button.dataset.nombre, Number(button.dataset.precio));
            if (!row) return;
            row.querySelector('.campo-nota').value = typeof item.nota === 'string' ? item.nota : '';
            var meats = Array.from(row.querySelectorAll('.selector-medallones input'));
            var meat = meats.find(function (input) { return input.value === String(item.medallones); });
            if (meat && !row.querySelector('.selector-medallones').hidden) meat.checked = true;
            else if (String(item.medallones || '0') !== '0') unavailable = true;
            var extras = Array.from(row.querySelectorAll('.chips-adicionales input'));
            (Array.isArray(item.extras) ? item.extras : []).forEach(function (id) {
                var input = extras.find(function (candidate) { return candidate.value === String(id); });
                if (input) input.checked = true;
                else unavailable = true;
            });
        });
        cambiarEntrega();
        mostrarLinkMaps();
        calcularTotal();
        restoring = false;
        show('Retomaste tu pedido a medio cargar', unavailable);
        help.textContent = unavailable
            ? 'Algunos productos o extras ya no están disponibles y no se pudieron recuperar. Revisá el pedido antes de crearlo.'
            : 'Conservamos los datos de esta pestaña. El total usa los precios y tarifas actuales; revisalo antes de crear el pedido.';
    }

    function reset() {
        restoring = true;
        form.reset();
        document.getElementById('listaProductos').innerHTML = '';
        document.getElementById('mensajeWhatsapp').value = '';
        document.querySelector('.card-pegar').open = false;
        document.getElementById('resultadoMensaje').hidden = true;
        token = window.crypto.randomUUID();
        document.getElementById('borradorToken').value = token;
        cambiarEntrega();
        mostrarLinkMaps();
        calcularTotal();
        restoring = false;
        notice.hidden = true;
        notice.classList.remove('is-warning');
        help.textContent = 'Podés ir a otra sección y volver en esta pestaña. Todavía no es un pedido creado.';
    }

    if (draft && !storageProblem) restore(draft);
    else if (storageProblem) show('No se pudo recuperar el borrador; no se borró lo guardado', true);
    form.addEventListener('input', save);
    form.addEventListener('change', save);
    form.addEventListener('submit', save); // No se borra al enviar: puede fallar la validación o la conexión.
    document.addEventListener('pedido:actualizado', save);
    window.addEventListener('pagehide', save);
    document.addEventListener('visibilitychange', function () { if (document.hidden) save(); });
    document.getElementById('descartarBorrador').addEventListener('click', function () {
        if (!window.confirm('¿Descartar este borrador? Se vaciará el pedido que todavía no creaste.')) return;
        try { window.sessionStorage.removeItem(key); }
        catch (error) { show('No se pudo descartar el borrador', true); return; }
        reset();
        document.getElementById('clienteNombre').focus();
    });
    window.addEventListener('pageshow', function (event) {
        // Volver atrás después de crear no debe revivir un pedido ya confirmado.
        if (event.persisted) {
            try { if (!window.sessionStorage.getItem(key)) reset(); }
            catch (error) { show('No se pudo comprobar el borrador', true); }
        }
    });
});
