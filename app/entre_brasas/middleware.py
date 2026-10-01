"""No admite cambios nuevos mientras termina de cerrar el servidor."""
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse

from .servidor_local import estado


class BloqueoDuranteApagadoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        permitida = request.path in (reverse('apagar_sistema'), reverse('estado_sistema'))
        recurso = request.method in ('GET', 'HEAD') and request.path.startswith(settings.STATIC_URL)
        if estado()['apagando'] and not permitida and not recurso:
            # Algunas acciones históricas usan GET: bloqueamos también esas rutas.
            if request.method in ('GET', 'HEAD'):
                return render(request, 'sistema/bloqueado.html', status=503)
            response = JsonResponse({
                'error': 'Sistema apagado. No se pueden guardar cambios.',
                **estado(),
            }, status=503)
            response['Cache-Control'] = 'no-store'
            return response
        return self.get_response(request)
