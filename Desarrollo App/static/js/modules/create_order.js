document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('orderForm');
    const container = document.getElementById('productosContainer');
    const addBtn = document.getElementById('addProducto');
    const retiroLocal = document.getElementById('retiroLocal');
    const envioFields = document.getElementById('envioFields');
    const distanciaInput = document.getElementById('distancia');

    let productoIndex = 0;

    // Load hamburgers into select
    function loadHamburgers() {
        const hamburgers = HamburgerService.getActive();
        document.querySelectorAll('.hamburger-select').forEach(select => {
            select.innerHTML = '<option value="">Seleccionar hamburguesa...</option>';
            hamburgers.forEach(h => {
                const opt = document.createElement('option');
                opt.value = h.id;
                opt.textContent = `${h.nombre} - $${h.precio_base.toLocaleString('es-AR')}`;
                opt.dataset.precio = h.precio_base;
                opt.dataset.incluyePapas = h.incluye_papas;
                select.appendChild(opt);
            });
        });
    }

    // Load addons for selected hamburger
    function loadAddons(hamburgerId, addonsContainer) {
        const addons = AddonService.getByHamburgerId(hamburgerId);
        addonsContainer.innerHTML = '<label>Adicionales:</label>';
        addons.forEach(a => {
            const label = document.createElement('label');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'addon-checkbox';
            checkbox.value = a.id;
            checkbox.dataset.precio = a.precio;
            checkbox.dataset.nombre = a.nombre;
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(` ${a.nombre} ($${a.precio.toLocaleString('es-AR')})`));
            addonsContainer.appendChild(label);
        });
    }

    // Calculate totals
    function calculateTotals() {
        let subtotalProductos = 0;
        let subtotalAdicionales = 0;

        document.querySelectorAll('.producto-item').forEach(item => {
            const select = item.querySelector('.hamburger-select');
            const cantidad = parseInt(item.querySelector('.cantidad-input').value) || 0;
            const precio = parseInt(select.options[select.selectedIndex]?.dataset?.precio || 0);

            subtotalProductos += precio * cantidad;

            item.querySelectorAll('.addon-checkbox:checked').forEach(cb => {
                subtotalAdicionales += parseInt(cb.dataset.precio) * cantidad;
            });
        });

        // Calculate shipping
        let costoEnvio = 0;
        const retiro = retiroLocal.value === 'true';
        if (!retiro) {
            const distancia = parseFloat(distanciaInput.value) || 0;
            const config = ConfigService.get();
            if (distancia >= config.distancia_minima) {
                costoEnvio = distancia * config.tarifa_km;
                if (costoEnvio < config.costo_minimo_envio) {
                    costoEnvio = config.costo_minimo_envio;
                }
            }
        }

        document.getElementById('subtotalProductos').textContent = subtotalProductos.toLocaleString('es-AR');
        document.getElementById('subtotalAdicionales').textContent = subtotalAdicionales.toLocaleString('es-AR');
        document.getElementById('costoEnvio').textContent = costoEnvio.toLocaleString('es-AR');
        document.getElementById('totalEnvio').textContent = costoEnvio.toLocaleString('es-AR');
        document.getElementById('totalGeneral').textContent = (subtotalProductos + subtotalAdicionales + costoEnvio).toLocaleString('es-AR');
    }

    // Add new product
    function addProduct() {
        const div = document.createElement('div');
        div.className = 'producto-item';
        div.dataset.index = productoIndex++;
        div.innerHTML = `
            <div>
                <label>Hamburguesa *</label>
                <select class="hamburger-select" required>
                    <option value="">Seleccionar hamburguesa...</option>
                </select>
            </div>
            <div>
                <label>Cantidad *</label>
                <input type="number" class="cantidad-input" value="1" min="1" required>
            </div>
            <div class="addons-container">
                <label>Adicionales:</label>
            </div>
            <button type="button" class="btn btn-danger btn-remove-producto">Eliminar producto</button>
        `;
        container.appendChild(div);
        loadHamburgers();
        setupProductEvents(div);
    }

    // Setup events for product item
    function setupProductEvents(item) {
        const select = item.querySelector('.hamburger-select');
        const addonsContainer = item.querySelector('.addons-container');
        const removeBtn = item.querySelector('.btn-remove-producto');
        const cantidadInput = item.querySelector('.cantidad-input');

        select.addEventListener('change', function() {
            const hamburgerId = parseInt(this.value);
            if (hamburgerId) {
                loadAddons(hamburgerId, addonsContainer);
            } else {
                addonsContainer.innerHTML = '<label>Adicionales:</label>';
            }
            calculateTotals();
        });

        removeBtn.addEventListener('click', function() {
            if (document.querySelectorAll('.producto-item').length > 1) {
                item.remove();
                calculateTotals();
            }
        });

        cantidadInput.addEventListener('change', calculateTotals);
        addonsContainer.addEventListener('change', calculateTotals);
    }

    // Toggle shipping fields
    retiroLocal.addEventListener('change', function() {
        const retiro = this.value === 'true';
        envioFields.style.display = retiro ? 'none' : 'block';
        calculateTotals();
    });

    distanciaInput.addEventListener('input', calculateTotals);

    // Form submit
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const cliente = {
            nombre: document.getElementById('clienteNombre').value,
            telefono: document.getElementById('clienteTelefono').value,
            direccion: document.getElementById('clienteDireccion').value
        };

        const productos = [];
        document.querySelectorAll('.producto-item').forEach(item => {
            const select = item.querySelector('.hamburger-select');
            const hamburgerId = parseInt(select.value);
            if (!hamburgerId) return;

            const hamburger = HamburgerService.getById(hamburgerId);
            const cantidad = parseInt(item.querySelector('.cantidad-input').value);
            const adicionales = [];

            item.querySelectorAll('.addon-checkbox:checked').forEach(cb => {
                adicionales.push({
                    adicional_id: parseInt(cb.value),
                    nombre: cb.dataset.nombre,
                    precio: parseInt(cb.dataset.precio)
                });
            });

            productos.push({
                hamburguesa_id: hamburgerId,
                nombre: hamburger.nombre,
                cantidad,
                precio_base: hamburger.precio_base,
                adicionales
            });
        });

        if (productos.length === 0) {
            alert('Debe agregar al menos un producto');
            return;
        }

        const retiro = retiroLocal.value === 'true';
        const distancia = parseFloat(distanciaInput.value) || 0;
        const config = ConfigService.get();
        let costoEnvio = 0;

        if (!retiro && distancia >= config.distancia_minima) {
            costoEnvio = distancia * config.tarifa_km;
            if (costoEnvio < config.costo_minimo_envio) {
                costoEnvio = config.costo_minimo_envio;
            }
        }

        const metodoPago = document.querySelector('input[name="metodoPago"]:checked')?.value;

        const orderData = {
            cliente,
            productos,
            envio: {
                distancia_km: distancia,
                costo_envio: costoEnvio,
                retiro_local: retiro
            },
            observaciones: document.getElementById('observaciones').value,
            metodo_pago: metodoPago,
            total: parseInt(document.getElementById('totalGeneral').textContent.replace(/\./g, ''))
        };

        OrderService.create(orderData);
        window.location.href = '/pedidos/cola/';
    });

    // Initialize
    loadHamburgers();
    setupProductEvents(container.querySelector('.producto-item'));
});
