document.addEventListener('DOMContentLoaded', function() {
    const ingredientsList = document.getElementById('ingredientsList');
    const movementsTable = document.getElementById('movementsTable');
    const form = document.getElementById('movementForm');
    const ingredienteSelect = document.getElementById('ingrediente');
    const filterIngrediente = document.getElementById('filterIngrediente');

    // Load ingredients
    function loadIngredients() {
        const ingredients = IngredientService.getActive();
        ingredienteSelect.innerHTML = '';
        filterIngrediente.innerHTML = '<option value="">Todos los ingredientes</option>';
        ingredients.forEach(i => {
            const opt = document.createElement('option');
            opt.value = i.id;
            opt.textContent = `${i.nombre} (${i.stock_actual} ${i.unidad})`;
            ingredienteSelect.appendChild(opt);

            const opt2 = opt.cloneNode(true);
            filterIngrediente.appendChild(opt2);
        });
    }

    // Render ingredients list
    function renderIngredientsList() {
        const ingredients = IngredientService.getActive();
        let html = '<table><tr><th>Ingrediente</th><th>Stock</th><th>Unidad</th><th>Minimo</th><th>Acciones</th></tr>';
        ingredients.forEach(i => {
            const isLow = i.stock_actual < i.stock_minimo;
            html += `<tr class="${isLow ? 'highlight' : ''}">
                <td><strong>${i.nombre}</strong></td>
                <td>${isLow ? '⚠ ' : ''}${i.stock_actual}</td>
                <td>${i.unidad}</td>
                <td>${i.stock_minimo}</td>
                <td>
                    <button class="btn btn-success btn-entry" data-id="${i.id}">+ Entrada</button>
                    <button class="btn btn-danger btn-exit" data-id="${i.id}">- Salida</button>
                </td>
            </tr>`;
        });
        html += '</table>';
        ingredientsList.innerHTML = html;

        document.querySelectorAll('.btn-entry').forEach(btn => {
            btn.addEventListener('click', function() {
                ingredienteSelect.value = this.dataset.id;
                document.getElementById('tipo').value = 'entrada';
                document.getElementById('cantidad').focus();
            });
        });

        document.querySelectorAll('.btn-exit').forEach(btn => {
            btn.addEventListener('click', function() {
                ingredienteSelect.value = this.dataset.id;
                document.getElementById('tipo').value = 'salida';
                document.getElementById('cantidad').focus();
            });
        });
    }

    // Render movements
    function renderMovements(filters = {}) {
        const movements = InventoryService.getMovements(filters);
        let html = '<table><tr><th>Fecha</th><th>Ingrediente</th><th>Tipo</th><th>Cantidad</th><th>Motivo</th></tr>';
        movements.forEach(m => {
            const fecha = new Date(m.fecha);
            html += `<tr>
                <td>${fecha.toLocaleDateString('es-AR')} ${fecha.toLocaleTimeString('es-AR', {hour: '2-digit', minute:'2-digit'})}</td>
                <td>${m.ingrediente_nombre}</td>
                <td><span class="badge ${m.tipo === 'entrada' ? 'badge-entregado' : 'badge-cancelado'}">${m.tipo === 'entrada' ? 'Entrada' : 'Salida'}</span></td>
                <td>${m.tipo === 'entrada' ? '+' : '-'}${m.cantidad} ${m.unidad}</td>
                <td>${m.motivo}</td>
            </tr>`;
        });
        html += '</table>';
        movementsTable.innerHTML = html;
    }

    // Form submit
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const ingredienteId = parseInt(ingredienteSelect.value);
        const tipo = document.getElementById('tipo').value;
        const cantidad = parseFloat(document.getElementById('cantidad').value);
        const motivo = document.getElementById('motivo').value;

        if (tipo === 'entrada') {
            InventoryService.addEntry(ingredienteId, cantidad, motivo);
        } else {
            const result = InventoryService.addExit(ingredienteId, cantidad, motivo);
            if (!result) {
                alert('No hay suficiente stock para esta salida');
                return;
            }
        }

        form.reset();
        renderIngredientsList();
        renderMovements();
    });

    // Filter
    document.getElementById('btnFilter').addEventListener('click', function() {
        const filters = {};
        if (filterIngrediente.value) filters.ingrediente_id = parseInt(filterIngrediente.value);
        if (document.getElementById('filterTipo').value) filters.tipo = document.getElementById('filterTipo').value;
        if (document.getElementById('filterFechaDesde').value) filters.fecha_desde = document.getElementById('filterFechaDesde').value;
        if (document.getElementById('filterFechaHasta').value) filters.fecha_hasta = document.getElementById('filterFechaHasta').value;
        renderMovements(filters);
    });

    // Initialize
    loadIngredients();
    renderIngredientsList();
    renderMovements();
});
