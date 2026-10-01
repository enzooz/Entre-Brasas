"""
Vista general del proyecto.
"""
from django.db.models import Count, F, Q, Sum
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from . import servidor_local

from inventario.models import ingredientes_del_menu_activo
from menu.models import Hamburguesa
from pedidos.models import Pedido


@never_cache
@require_http_methods(['GET'])
def estado_sistema(request):
    return JsonResponse(servidor_local.estado())


@require_http_methods(['GET', 'POST'])
def apagar_sistema(request):
    """GET confirma; solamente POST con CSRF apaga este servidor local."""
    if request.META.get('REMOTE_ADDR') not in ('127.0.0.1', '::1'):
        return HttpResponseForbidden('El sistema solo se puede apagar desde esta computadora.')
    if not servidor_local.disponible():
        return render(request, 'sistema/apagar.html', {'no_disponible': True}, status=409)
    if request.method == 'POST':
        if not servidor_local.solicitar_apagado():
            return render(request, 'sistema/apagar.html', {'no_disponible': True}, status=409)
        return render(request, 'sistema/apagar.html', {'apagado': True})
    return render(request, 'sistema/apagar.html')


def inicio(request):
    """
    Atiende la direccion raiz del sitio.

    Ofrece accesos por tarea y un resumen de los datos reales del local.
    """
    hoy = timezone.localdate()
    abiertos = Pedido.objects.exclude(estado__in=['entregado', 'cancelado'])
    resumen = abiertos.aggregate(
        total=Count('pk'),
        pendientes=Count('pk', filter=Q(estado='pendiente')),
        preparando=Count('pk', filter=Q(estado='en_preparacion')),
        en_camino=Count('pk', filter=Q(estado='en_camino')),
    )
    ventas = Pedido.objects.filter(estado='entregado', fecha_creacion__date=hoy).aggregate(
        total=Sum('total'), cantidad=Count('pk'),
    )
    faltantes = ingredientes_del_menu_activo().filter(stock_actual__lt=F('stock_minimo'))
    return render(request, 'inicio.html', {
        'hoy': hoy, 'resumen': resumen,
        'ventas_hoy': ventas['total'] or 0,
        'entregados_hoy': ventas['cantidad'],
        'pedidos_recientes': abiertos[:4],
        'faltantes_count': faltantes.count(),
        'faltantes_inicio': faltantes[:3],
        'productos_activos': Hamburguesa.objects.filter(activa=True).count(),
    })
