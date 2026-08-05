document.addEventListener('DOMContentLoaded', function() {
    const hamburgerSelect = document.getElementById('hamburgerSelect');
    const recipeSection = document.getElementById('recipeSection');
    const recipeTable = document.getElementById('recipeTable');
    const totalCost = document.getElementById('totalCost');
    const ingredientSelect = document.getElementById('ingredientSelect');
    const rentabilitySummary = document.getElementById('rentabilitySummary');

    // Load hamburgers
    const hamburgers = HamburgerService.getAll();
    hamburgers.forEach(h => {
        const opt = document.createElement('option');
        opt.value = h.id;
        opt.textContent = h.nombre;
        hamburgerSelect.appendChild(opt);
    });

    // Load ingredients for add form
    const ingredients = IngredientService.getActive();
    ingredients.forEach(i => {
        const opt = document.createElement('option');
        opt.value = i.id;
        opt.textContent = `${i.nombre} ($${i.precio_compra}/${i.unidad})`;
        ingredientSelect.appendChild(opt);
    });

    // Render recipe
    function renderRecipe(hamburgerId) {
        const recipe = RecipeService.getRecipe(hamburgerId);
        const hamburger = HamburgerService.getById(hamburgerId);
        if (!hamburger) return;

        document.getElementById('hamburgerName').textContent = hamburger.nombre;
        recipeSection.style.display = 'block';

        let html = '';
        let total = 0;

        recipe.forEach(item => {
            const ingredient = IngredientService.getById(item.ingrediente_id);
            const cost = ingredient ? ingredient.precio_compra * item.cantidad : 0;
            total += cost;
            html += `<tr>
                <td>${item.nombre}</td>
                <td>${item.cantidad}</td>
                <td>${item.unidad}</td>
                <td>$${cost.toLocaleString('es-AR')}</td>
                <td><button class="btn btn-danger btn-remove" data-id="${item.ingrediente_id}">Eliminar</button></td>
            </tr>`;
        });

        recipeTable.innerHTML = html;
        totalCost.textContent = `$${total.toLocaleString('es-AR')}`;

        // Calculate rentability
        const config = ConfigService.get();
        const costWithLabor = total + (config.costo_hora_mano_obra / 60 * 10);
        const margin = hamburger.precio_base > 0 ? ((hamburger.precio_base - costWithLabor) / costWithLabor * 100) : 0;
        const profit = hamburger.precio_base - costWithLabor;

        rentabilitySummary.innerHTML = `
            <div class="cost-summary">
                <p><strong>Precio de venta:</strong> $${hamburger.precio_base.toLocaleString('es-AR')}</p>
                <p><strong>Costo ingredientes:</strong> $${total.toLocaleString('es-AR')}</p>
                <p><strong>Costo mano de obra:</strong> $${(config.costo_hora_mano_obra / 60 * 10).toLocaleString('es-AR')}</p>
                <p><strong>Costo total:</strong> $${costWithLabor.toLocaleString('es-AR')}</p>
                <p class="total-highlight">Margen: ${margin.toFixed(1)}% | Ganancia: $${profit.toLocaleString('es-AR')}</p>
            </div>
        `;

        // Remove buttons
        document.querySelectorAll('.btn-remove').forEach(btn => {
            btn.addEventListener('click', function() {
                const ingredientId = parseInt(this.dataset.id);
                RecipeService.removeIngredient(hamburgerId, ingredientId);
                renderRecipe(hamburgerId);
            });
        });
    }

    // Hamburger select change
    hamburgerSelect.addEventListener('change', function() {
        renderRecipe(parseInt(this.value));
    });

    // Add ingredient form
    document.getElementById('addIngredientForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const hamburgerId = parseInt(hamburgerSelect.value);
        const ingredientId = parseInt(ingredientSelect.value);
        const ingredient = IngredientService.getById(ingredientId);
        const cantidad = parseFloat(document.getElementById('cantidad').value);
        const unidad = document.getElementById('unidadSelect').value;

        RecipeService.addIngredient(hamburgerId, {
            ingrediente_id: ingredientId,
            nombre: ingredient.nombre,
            cantidad,
            unidad
        });

        document.getElementById('cantidad').value = '';
        renderRecipe(hamburgerId);
    });

    // Initialize
    if (hamburgers.length > 0) {
        renderRecipe(hamburgers[0].id);
    }
});
