document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.getElementById('ingredientsTable');

    function renderIngredients() {
        const ingredients = IngredientService.getAll();
        tbody.innerHTML = '';

        ingredients.forEach(i => {
            const isLow = i.stock_actual < i.stock_minimo;
            const tr = document.createElement('tr');
            tr.className = isLow ? 'highlight' : '';
            tr.innerHTML = `
                <td><strong>${i.nombre}</strong></td>
                <td>${isLow ? '⚠ ' : ''}${i.stock_actual}</td>
                <td>${i.unidad}</td>
                <td>${i.stock_minimo}</td>
                <td><span class="badge ${i.activo ? 'badge-entregado' : 'badge-cancelado'}">${i.activo ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                    ${i.activo ? `
                        <a href="/inventario/ingredientes/${i.id}/editar/" class="btn btn-info">Editar</a>
                        <button class="btn btn-danger btn-deactivate" data-id="${i.id}">Desactivar</button>
                    ` : '<span class="badge badge-cancelado">Inactivo</span>'}
                </td>
            `;
            tbody.appendChild(tr);
        });

        document.querySelectorAll('.btn-deactivate').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = parseInt(this.dataset.id);
                if (confirm('Esta seguro de desactivar este ingrediente?')) {
                    IngredientService.deactivate(id);
                    renderIngredients();
                }
            });
        });
    }

    renderIngredients();
});
