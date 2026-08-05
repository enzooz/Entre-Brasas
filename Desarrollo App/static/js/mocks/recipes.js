const RECIPES_MOCK = {
    1: [ // Clasica
        { ingrediente_id: 1, nombre: "Carne molida", cantidad: 0.2, unidad: "kg" },
        { ingrediente_id: 2, nombre: "Pan de hamburguesa", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 3, nombre: "Lechuga", cantidad: 0.05, unidad: "kg" },
        { ingrediente_id: 4, nombre: "Tomate", cantidad: 2, unidad: "unidades" },
        { ingrediente_id: 5, nombre: "Cebolla", cantidad: 1, unidad: "unidades" }
    ],
    2: [ // Especial
        { ingrediente_id: 1, nombre: "Carne molida", cantidad: 0.4, unidad: "kg" },
        { ingrediente_id: 2, nombre: "Pan de hamburguesa", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 6, nombre: "Bacon", cantidad: 0.1, unidad: "kg" },
        { ingrediente_id: 7, nombre: "Cheddar", cantidad: 0.1, unidad: "kg" },
        { ingrediente_id: 5, nombre: "Cebolla", cantidad: 1, unidad: "unidades" }
    ],
    3: [ // Veggie
        { ingrediente_id: 16, nombre: "Medallon de verduras", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 2, nombre: "Pan de hamburguesa", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 8, nombre: "Palta", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 3, nombre: "Lechuga", cantidad: 0.05, unidad: "kg" }
    ],
    4: [ // Doble Bacon
        { ingrediente_id: 1, nombre: "Carne molida", cantidad: 0.4, unidad: "kg" },
        { ingrediente_id: 2, nombre: "Pan de hamburguesa", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 6, nombre: "Bacon", cantidad: 0.2, unidad: "kg" },
        { ingrediente_id: 7, nombre: "Cheddar", cantidad: 0.1, unidad: "kg" },
        { ingrediente_id: 11, nombre: "Salsa BBQ", cantidad: 0.05, unidad: "L" }
    ],
    5: [ // Pollo Crispy
        { ingrediente_id: 9, nombre: "Pollo (pechuga)", cantidad: 0.2, unidad: "kg" },
        { ingrediente_id: 2, nombre: "Pan de hamburguesa", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 3, nombre: "Lechuga", cantidad: 0.05, unidad: "kg" },
        { ingrediente_id: 10, nombre: "Mayonesa", cantidad: 0.02, unidad: "L" }
    ],
    6: [ // BBQ
        { ingrediente_id: 1, nombre: "Carne molida", cantidad: 0.2, unidad: "kg" },
        { ingrediente_id: 2, nombre: "Pan de hamburguesa", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 6, nombre: "Bacon", cantidad: 0.1, unidad: "kg" },
        { ingrediente_id: 12, nombre: "Cebolla crispy", cantidad: 0.05, unidad: "kg" },
        { ingrediente_id: 11, nombre: "Salsa BBQ", cantidad: 0.05, unidad: "L" }
    ],
    7: [ // Hawaiana
        { ingrediente_id: 1, nombre: "Carne molida", cantidad: 0.2, unidad: "kg" },
        { ingrediente_id: 2, nombre: "Pan de hamburguesa", cantidad: 1, unidad: "unidades" },
        { ingrediente_id: 13, nombre: "Jamon", cantidad: 0.1, unidad: "kg" },
        { ingrediente_id: 14, nombre: "Pina", cantidad: 2, unidad: "unidades" },
        { ingrediente_id: 17, nombre: "Queso", cantidad: 0.05, unidad: "kg" }
    ]
};

const RecipeService = {
    getRecipe: (hamburgerId) => RECIPES_MOCK[hamburgerId] || [],
    setRecipe: (hamburgerId, recipe) => {
        RECIPES_MOCK[hamburgerId] = recipe;
        return recipe;
    },
    addIngredient: (hamburgerId, ingredient) => {
        if (!RECIPES_MOCK[hamburgerId]) RECIPES_MOCK[hamburgerId] = [];
        RECIPES_MOCK[hamburgerId].push(ingredient);
        return RECIPES_MOCK[hamburgerId];
    },
    removeIngredient: (hamburgerId, ingredientId) => {
        if (!RECIPES_MOCK[hamburgerId]) return false;
        RECIPES_MOCK[hamburgerId] = RECIPES_MOCK[hamburgerId].filter(i => i.ingrediente_id !== ingredientId);
        return true;
    },
    calculateCost: (hamburgerId) => {
        const recipe = RECIPES_MOCK[hamburgerId] || [];
        return recipe.reduce((total, item) => {
            const ingredient = INGREDIENTS_MOCK.find(i => i.id === item.ingrediente_id);
            return total + (ingredient ? ingredient.precio_compra * item.cantidad : 0);
        }, 0);
    }
};
