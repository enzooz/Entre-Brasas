"""
Vistas de la app Costos.

Calcula cuanto cuesta preparar cada hamburguesa y cuanta ganancia deja.

La cuenta es:
    costo de ingredientes  = suma de (cantidad de la receta x precio del ingrediente)
    costo de mano de obra  = (costo de la hora / 60) x minutos que lleva prepararla
    costo total            = ingredientes + mano de obra
    ganancia               = precio de venta - costo total
    margen                 = ganancia / precio de venta x 100
"""
from django.shortcuts import render

from menu.models import Hamburguesa
from config.models import Configuracion


# Minutos que se estima que lleva preparar una hamburguesa.
# Se usa para calcular cuanto de mano de obra le corresponde a cada una.
MINUTOS_DE_PREPARACION = 10


def ver_costos(request):
    """
    Pantalla de costos: una fila por hamburguesa con su costo y su ganancia.
    """
    configuracion = Configuracion.get_config()

    # Cuanto sale un minuto de trabajo.
    costo_por_minuto = configuracion.costo_hora_mano_obra / 60
    costo_mano_obra = round(costo_por_minuto * MINUTOS_DE_PREPARACION)

    filas = []

    for hamburguesa in Hamburguesa.objects.filter(activa=True):
        # --- Cuanto cuestan los ingredientes ---
        costo_ingredientes = 0

        # recetas es el related_name del modelo Receta: nos da todas las
        # lineas de receta de esta hamburguesa.
        for linea in hamburguesa.recetas.all():
            costo_de_esta_linea = linea.cantidad_requerida * linea.ingrediente.precio_compra
            costo_ingredientes = costo_ingredientes + costo_de_esta_linea

        costo_ingredientes = round(costo_ingredientes)

        # --- Costo total y ganancia ---
        costo_total = costo_ingredientes + costo_mano_obra
        ganancia = hamburguesa.precio - costo_total

        # El margen es que porcentaje del precio de venta es ganancia.
        # Preguntamos antes de dividir para no dividir por cero.
        if hamburguesa.precio > 0:
            margen = round(ganancia / hamburguesa.precio * 100)
        else:
            margen = 0

        filas.append({
            'hamburguesa': hamburguesa,
            'tiene_receta': hamburguesa.recetas.exists(),
            'costo_ingredientes': costo_ingredientes,
            'costo_mano_obra': costo_mano_obra,
            'costo_total': costo_total,
            'ganancia': ganancia,
            'margen': margen,
        })

    return render(request, 'costos/ver_costos.html', {
        'filas': filas,
        'costo_hora_mano_obra': configuracion.costo_hora_mano_obra,
        'minutos_preparacion': MINUTOS_DE_PREPARACION,
    })
