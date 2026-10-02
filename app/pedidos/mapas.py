"""Geoapify por servidor: sin claves en respuestas, metros, caché y límite local.

El navegador sólo pide una búsqueda explícita o una ruta entre dos puntos.
No se almacenan ni modifican pedidos en estos endpoints.
"""
import hashlib
import json
import math
import threading
import time
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import caches
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_GET

from config.models import Configuracion

_cerrojo = threading.Lock()
_trabajos = threading.BoundedSemaphore(8)
_ultima_consulta = 0.0
CENTRO = (-27.455266, -58.992536)


class ErrorMapa(Exception):
    def __init__(self, mensaje, estado=503):
        self.estado = estado
        super().__init__(mensaje)


def coordenadas(latitud, longitud):
    try:
        if isinstance(latitud, bool) or isinstance(longitud, bool):
            raise ValueError
        lat, lon = float(latitud), float(longitud)
        if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError
        # Área de trabajo: Resistencia y alrededores (30 km del centro).
        a = math.sin(math.radians(lat - CENTRO[0]) / 2) ** 2
        a += math.cos(math.radians(lat)) * math.cos(math.radians(CENTRO[0])) * math.sin(math.radians(lon - CENTRO[1]) / 2) ** 2
        if 6371000 * 2 * math.asin(min(1, math.sqrt(a))) > 30000:
            raise ValueError
        return round(lat, 6), round(lon, 6)
    except (TypeError, ValueError, OverflowError):
        raise ErrorMapa('Elegí un punto de Resistencia o alrededores. Para otros destinos, ingresá la distancia manualmente.', 400) from None


def kilometros_para_envio(metros):
    """1340 metros → 1.3 km. Truncar, no redondear hacia otro tramo."""
    try:
        metros = Decimal(str(metros))
    except InvalidOperation:
        raise ValueError('Distancia inválida') from None
    if not metros.is_finite() or metros < 0 or metros >= 1000000:
        raise ValueError('Distancia fuera de rango')
    return format((metros / 1000).quantize(Decimal('0.1'), rounding=ROUND_DOWN), 'f')


def _consultar(recurso, parametros, clave, mosaico=False):
    # Reservar trabajadores para pedidos y estado local aunque el proveedor tarde.
    if not _trabajos.acquire(blocking=False):
        raise ErrorMapa('El servicio de mapas está ocupado. Probá nuevamente o ingresá kilómetros manualmente.', 429)
    try:
        return _consultar_con_turno(recurso, parametros, clave, mosaico)
    finally:
        _trabajos.release()


def _consultar_con_turno(recurso, parametros, clave, mosaico=False):
    global _ultima_consulta
    if not clave:
        raise ErrorMapa('Falta la clave de Geoapify. Cargala en Configuración o ingresá los kilómetros manualmente.')
    huella = hashlib.sha256((clave + recurso + json.dumps(parametros, sort_keys=True)).encode()).hexdigest()
    cache, control = caches['mapas'], caches['mapas_control']
    # Un solo proceso Waitress: serializa duplicados y limita a menos de 5 solicitudes/segundo.
    with _cerrojo:
        resultado = cache.get(huella)
        if resultado is not None:
            return resultado
        if control.get('pausa'):
            raise ErrorMapa('Geoapify no está disponible ahora. Ingresá la distancia manualmente y probá más tarde.', 429)
        dia = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        contador = 'consultas:' + dia
        cantidad = control.get(contador, 0)
        creditos = 'creditos_cuartos:' + dia
        gastados = control.get(creditos, cantidad * 4)
        costo = 1 if mosaico else 4  # Cuartos de crédito, sin errores de coma flotante.
        if gastados + costo > settings.MAPAS_LIMITE_DIARIO * 4:
            raise ErrorMapa('Se alcanzó el límite preventivo diario de consultas. Podés cargar los kilómetros manualmente.', 429)
        control.set(contador, cantidad + 1, 172800)
        control.set(creditos, gastados + costo, 172800)
        espera = 0.26 - (time.monotonic() - _ultima_consulta)
        if espera > 0:
            time.sleep(espera)
        _ultima_consulta = time.monotonic()
        host = 'https://maps.geoapify.com/v1/' if mosaico else 'https://api.geoapify.com/v1/'
        url = host + recurso + '?' + urlencode({**parametros, 'apiKey': clave})
        try:
            request = Request(url, headers={'User-Agent': 'EntreBrasas/1.0', 'Accept': 'image/png' if mosaico else 'application/json'})
            with urlopen(request, timeout=7) as respuesta:
                contenido = respuesta.read(1000001)
                if len(contenido) > 1000000:
                    raise ValueError('Respuesta demasiado grande')
                if mosaico:
                    if not contenido.startswith(b'\x89PNG\r\n\x1a\n'):
                        raise ValueError('Mosaico inválido')
                    cache.set(huella, contenido, 86400)
                    return contenido
                resultado = json.loads(contenido)
                if not isinstance(resultado, dict):
                    raise ValueError('Respuesta inválida')
            # Guardar sólo features: el proveedor puede repetir apiKey en properties.
            features = resultado.get('features')
            if not isinstance(features, list):
                raise ValueError('Respuesta inválida')
            resultado = {'features': features}
            cache.set(huella, resultado, 86400)
            return resultado
        except HTTPError as error:
            if error.code in (401, 403):
                raise ErrorMapa('Geoapify rechazó la clave. Revisala en Configuración; podés seguir con distancia manual.') from None
            if error.code == 429:
                control.set('pausa', True, 300)
                raise ErrorMapa('Geoapify alcanzó su límite de consultas. Cargá la distancia manualmente y probá más tarde.', 429) from None
            raise ErrorMapa('No se pudo consultar Geoapify. Ingresá los kilómetros manualmente.') from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise ErrorMapa('No hay respuesta del servicio de mapas. Ingresá los kilómetros manualmente.') from None


def _datos(request):
    if len(request.body) > 4096:
        raise ErrorMapa('La consulta es demasiado larga.', 400)
    try:
        datos = json.loads(request.body)
        if not isinstance(datos, dict):
            raise ValueError
        return datos
    except (ValueError, UnicodeError):
        raise ErrorMapa('Revisá los datos de la consulta.', 400) from None


@require_GET
def mosaico_mapa(request, z, x, y):
    """PNG cacheado por servidor; no exponer la clave en URLs del navegador."""
    try:
        if not 10 <= z <= 19 or not 0 <= x < 2 ** z or not 0 <= y < 2 ** z:
            raise ErrorMapa('Mosaico fuera de rango.', 400)
        # Sólo mosaicos que intersectan Resistencia y alrededores.
        lon_izq, lon_der = x / 2 ** z * 360 - 180, (x + 1) / 2 ** z * 360 - 180
        lat_sup = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / 2 ** z))))
        lat_inf = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / 2 ** z))))
        if lon_der < -59.55 or lon_izq > -58.35 or lat_sup < -27.95 or lat_inf > -26.95:
            raise ErrorMapa('El mapa está limitado a Resistencia y alrededores.', 400)
        if request.headers.get('Sec-Fetch-Site', 'same-origin') not in ('same-origin', 'none'):
            raise ErrorMapa('Abrí el mapa desde Entre Brasas.', 403)
        config = Configuracion.get_config()
        contenido = _consultar(f'tile/osm-carto/{z}/{x}/{y}.png', {}, config.geoapify_api_key, mosaico=True)
        respuesta = HttpResponse(contenido, content_type='image/png')
        respuesta['Cache-Control'] = 'private, max-age=86400'
        return respuesta
    except ErrorMapa as error:
        respuesta = JsonResponse({'error': str(error)}, status=error.estado)
        respuesta['Cache-Control'] = 'no-store'
        return respuesta


@never_cache
@require_POST
def buscar_direccion(request):
    try:
        datos = _datos(request)
        texto = datos.get('texto')
        if not isinstance(texto, str) or not 3 <= len(texto.strip()) <= 300 or '://' in texto:
            raise ErrorMapa('Escribí una calle y altura o un lugar; no un enlace de Google Maps.', 400)
        config = Configuracion.get_config()
        respuesta = _consultar('geocode/search', {
            'text': texto.strip(), 'lang': 'es', 'limit': 5,
            'filter': f'circle:{CENTRO[1]},{CENTRO[0]},30000',
            'bias': f'proximity:{config.local_longitud},{config.local_latitud}',
        }, config.geoapify_api_key)
        resultados = []
        for feature in respuesta.get('features', [])[:5]:
            try:
                propiedades = feature['properties']
                lat, lon = coordenadas(propiedades['lat'], propiedades['lon'])
                direccion = str(propiedades['formatted'])[:300]
                aproximada = propiedades.get('result_type') != 'building' or propiedades.get('rank', {}).get('match_type') not in ('full_match', 'match_by_building')
                resultados.append({'direccion': direccion, 'latitud': lat, 'longitud': lon, 'aproximada': aproximada})
            except (KeyError, TypeError, AttributeError, ErrorMapa):
                continue
        return JsonResponse({'resultados': resultados})
    except ErrorMapa as error:
        return JsonResponse({'error': str(error)}, status=error.estado)


@never_cache
@require_POST
def calcular_recorrido(request):
    try:
        datos = _datos(request)
        destino = coordenadas(datos.get('latitud'), datos.get('longitud'))
        config = Configuracion.get_config()
        origen = coordenadas(config.local_latitud, config.local_longitud)
        respuesta = _consultar('routing', {
            'waypoints': f'{origen[0]},{origen[1]}|{destino[0]},{destino[1]}',
            'mode': 'drive', 'units': 'metric', 'lang': 'es',
        }, config.geoapify_api_key)
        try:
            ruta = respuesta['features'][0]
            propiedades, geometria = ruta['properties'], ruta['geometry']
            if str(propiedades['distance_units']).lower() != 'meters' or geometria['type'] != 'MultiLineString':
                raise ValueError
            if isinstance(propiedades['distance'], bool):
                raise ValueError
            metros = float(propiedades['distance'])
            km = kilometros_para_envio(metros)
            lineas = geometria['coordinates']
            if not isinstance(lineas, list) or not lineas or sum(len(linea) for linea in lineas) > 10000:
                raise ValueError
            for linea in lineas:
                if len(linea) < 2:
                    raise ValueError
                for punto in linea:
                    if len(punto) < 2 or not all(math.isfinite(float(x)) for x in punto[:2]):
                        raise ValueError
                    if not -180 <= float(punto[0]) <= 180 or not -90 <= float(punto[1]) <= 90:
                        raise ValueError
            return JsonResponse({'distancia_metros': metros, 'distancia_km': km,
                'geometria': {'type': 'MultiLineString', 'coordinates': lineas}, 'origen': list(origen)})
        except (KeyError, IndexError, TypeError, ValueError, OverflowError):
            raise ErrorMapa('No se encontró un recorrido válido en metros. Comprobá el destino o ingresá kilómetros manualmente.') from None
    except ErrorMapa as error:
        return JsonResponse({'error': str(error)}, status=error.estado)
