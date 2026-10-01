/* Busca en la base local; completar no guarda ni crea un pedido. */
document.addEventListener('DOMContentLoaded', function () {
    var search = document.getElementById('buscarCliente');
    if (!search) return;
    var status = document.getElementById('estadoClientes');
    var results = document.getElementById('resultadosClientes');
    var chosen = document.getElementById('clienteGuardadoId');
    var name = document.getElementById('clienteNombre');
    var phone = document.getElementById('clienteTelefono');
    var address = document.getElementById('clienteDireccion');
    var distance = document.getElementById('distancia');
    var sequence = 0, timer, controller;

    function cancel() {
        sequence++;
        window.clearTimeout(timer);
        if (controller) controller.abort();
        results.replaceChildren();
        results.hidden = true;
    }

    function refresh() {
        mostrarLinkMaps();
        calcularTotal(); // También actualiza el resumen y guarda el borrador.
    }

    function choose(customer) {
        cancel();
        chosen.value = String(customer.id);
        name.value = customer.nombre;
        phone.value = customer.telefono;
        if (address.value !== customer.direccion) distance.value = '';
        address.value = customer.direccion;
        status.textContent = 'Datos de ' + customer.nombre + ' completados. Revisá teléfono, dirección y distancia antes de crear el pedido.';
        refresh();
        name.focus();
    }

    async function lookup() {
        cancel();
        var query = search.value.trim();
        if (query.length < 2) {
            status.textContent = query ? 'Escribí al menos 2 caracteres para buscar.' : '';
            return;
        }
        var current = sequence;
        controller = new AbortController();
        var requestController = controller;
        var timeout = window.setTimeout(function () { requestController.abort(); }, 5000);
        status.textContent = 'Buscando clientes…';
        try {
            var response = await fetch(search.dataset.url + '?q=' + encodeURIComponent(query), {signal: controller.signal, cache: 'no-store'});
            if (!response.ok) throw new Error('No se pudo buscar');
            var data = await response.json();
            if (current !== sequence || query !== search.value.trim()) return;
            if (!Array.isArray(data.clientes)) throw new Error('Respuesta inválida');
            data.clientes.forEach(function (customer) {
                var button = document.createElement('button');
                button.type = 'button';
                button.className = 'customer-result';
                var title = document.createElement('strong');
                title.textContent = customer.nombre;
                var detail = document.createElement('span');
                detail.textContent = [customer.telefono || 'Sin teléfono', customer.direccion || 'Sin dirección guardada'].join(' · ');
                button.append(title, detail);
                button.addEventListener('click', function () { choose(customer); });
                results.appendChild(button);
            });
            results.hidden = !data.clientes.length;
            status.textContent = data.clientes.length ? 'Elegí un cliente para completar sus datos.' : 'No encontramos clientes. Podés cargar los datos abajo; se guardarán al crear el pedido.';
        } catch (error) {
            if (current === sequence) status.textContent = 'No se pudo buscar. Tocá Buscar para reintentar o cargá los datos manualmente.';
        } finally {
            window.clearTimeout(timeout);
        }
    }

    search.addEventListener('input', function () {
        cancel();
        status.textContent = '';
        timer = window.setTimeout(lookup, 250);
    });
    search.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') { event.preventDefault(); lookup(); }
        if (event.key === 'Escape') { cancel(); status.textContent = ''; }
    });
    document.getElementById('botonBuscarCliente').addEventListener('click', lookup);
    document.getElementById('clienteNuevo').addEventListener('click', function () {
        cancel();
        chosen.value = search.value = name.value = phone.value = address.value = '';
        distance.value = '';
        status.textContent = 'Cliente nuevo: completá los datos abajo.';
        refresh();
        name.focus();
    });
    function manual() {
        chosen.value = '';
        status.textContent = 'Datos editados. Se guardarán al crear el pedido, sin cambiar pedidos anteriores.';
    }
    name.addEventListener('input', manual);
    phone.addEventListener('input', manual);
    document.addEventListener('cliente:carga-manual', manual);
    document.getElementById('formPedido').addEventListener('reset', function () {
        cancel();
        search.value = status.textContent = '';
    });
});
