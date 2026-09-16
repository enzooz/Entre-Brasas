"""
Vista del app "reports" (reportes de ventas).

ATENCIÓN: esta vista NO consulta la base de datos. Solo devuelve el HTML.
Todos los números que se ven en pantalla los calcula el JavaScript
(static/js/modules/reports.js) a partir de datos falsos hardcodeados
en static/js/mocks/orders.js.

O sea: la pantalla de reportes hoy muestra data inventada, no las ventas reales.
Para conectarla habría que consultar Order acá y pasarle los totales al template.
"""

from django.shortcuts import render


def sales_reports(request):
    return render(request, 'reports/sales_reports.html')
