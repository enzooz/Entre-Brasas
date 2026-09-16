"""
Vista del app "costs" (costos y márgenes por producto).

ATENCIÓN: igual que reports, esta vista solo renderiza el HTML.
El cálculo de costo por hamburguesa (ingredientes + mano de obra) y el margen
lo hace static/js/costs.js usando los mocks de JavaScript, no la base de datos.

Para que sea real habría que calcularlo en Python: recorrer las Recipe del
producto, multiplicar por Ingredient.precio_compra y sumarle la mano de obra
de SystemConfig.
"""

from django.shortcuts import render


def costs_view(request):
    return render(request, 'costs/costs_view.html')
