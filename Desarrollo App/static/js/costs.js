document.addEventListener('DOMContentLoaded', function() {
    const filterProduct = document.getElementById('filterProduct');
    const costsTable = document.getElementById('costsTable');
    const summary = document.getElementById('summary');

    // Load hamburgers into filter
    const hamburgers = HamburgerService.getAll();
    hamburgers.forEach(h => {
        const opt = document.createElement('option');
        opt.value = h.id;
        opt.textContent = h.nombre;
        filterProduct.appendChild(opt);
    });

    function calculateCosts(hamburgerId) {
        const hamburger = HamburgerService.getById(hamburgerId);
        if (!hamburger) return null;

        const recipe = RecipeService.getRecipe(hamburgerId);
        const ingredientCost = recipe.reduce((total, item) => {
            const ingredient = INGREDIENTS_MOCK.find(i => i.id === item.ingrediente_id);
            return total + (ingredient ? ingredient.precio_compra * item.cantidad : 0);
        }, 0);

        const config = ConfigService.get();
        const laborCost = config.costo_hora_mano_obra / 60 * 10; // 10 min estimado
        const totalCost = ingredientCost + laborCost;
        const margin = hamburger.precio_base > 0 ? ((hamburger.precio_base - totalCost) / totalCost * 100) : 0;
        const profit = hamburger.precio_base - totalCost;

        return {
            nombre: hamburger.nombre,
            precio_venta: hamburger.precio_base,
            costo_ingredientes: ingredientCost,
            costo_mano_obra: laborCost,
            costo_total: totalCost,
            margen: margin,
            ganancia: profit
        };
    }

    function renderCosts() {
        const filterId = filterProduct.value ? parseInt(filterProduct.value) : null;
        const ids = filterId ? [filterId] : hamburgers.map(h => h.id);

        let html = '<table><tr><th>Producto</th><th>Precio Venta</th><th>Costo Ingred.</th><th>Costo MO</th><th>Costo Total</th><th>Margen</th><th>Ganancia</th></tr>';
        const allCosts = [];

        ids.forEach(id => {
            const costs = calculateCosts(id);
            if (costs) {
                allCosts.push(costs);
                const marginClass = costs.margen >= 100 ? 'badge-entregado' : costs.margen >= 50 ? 'badge-pendiente' : 'badge-cancelado';
                html += `<tr>
                    <td><strong>${costs.nombre}</strong></td>
                    <td>$${costs.precio_venta.toLocaleString('es-AR')}</td>
                    <td>$${costs.costo_ingredientes.toLocaleString('es-AR')}</td>
                    <td>$${costs.costo_mano_obra.toLocaleString('es-AR')}</td>
                    <td>$${costs.costo_total.toLocaleString('es-AR')}</td>
                    <td><span class="badge ${marginClass}">${costs.margen.toFixed(1)}%</span></td>
                    <td>$${costs.ganancia.toLocaleString('es-AR')}</td>
                </tr>`;
            }
        });
        html += '</table>';
        costsTable.innerHTML = html;

        // Summary
        if (allCosts.length > 0) {
            const avgMargin = allCosts.reduce((sum, c) => sum + c.margen, 0) / allCosts.length;
            const mostProfitable = allCosts.reduce((a, b) => a.ganancia > b.ganancia ? a : b);
            const leastProfitable = allCosts.reduce((a, b) => a.ganancia < b.ganancia ? a : b);

            summary.innerHTML = `
                <div class="summary-card">
                    <div class="value">${avgMargin.toFixed(1)}%</div>
                    <div class="label">Margen promedio</div>
                </div>
                <div class="summary-card">
                    <div class="value">${mostProfitable.nombre}</div>
                    <div class="label">Mas rentable</div>
                </div>
                <div class="summary-card">
                    <div class="value">${leastProfitable.nombre}</div>
                    <div class="label">Menos rentable</div>
                </div>
            `;
        }
    }

    filterProduct.addEventListener('change', renderCosts);
    renderCosts();
});
