import json
import math
import threading
import time
from datetime import datetime, timezone
from decimal import Decimal
from unittest import mock
from urllib.error import HTTPError, URLError

from django.core.cache import caches
from django.test import TestCase, Client, override_settings

from config.forms import ConfiguracionForm
from config.models import Configuracion
from . import mapas
from .calculos import calcular_envio


@override_settings(CACHES={
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'test-default'},
    'mapas': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'test-mapas'},
    'mapas_control': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'test-control'},
})
class MapasTests(TestCase):
    def setUp(self):
        self.config = Configuracion.get_config()
        self.config.geoapify_api_key = 'clave-de-prueba'
        self.config.save()
        for alias in ('mapas', 'mapas_control'):
            caches[alias].clear()

    def post(self, path, data):
        return self.client.post('/pedidos/mapas/' + path + '/', json.dumps(data), content_type='application/json')

    def response(self, data):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(data).encode()
        return response

    def test_metros_a_decima_km_sin_millas_ni_redondeo(self):
        for metros, km in [(100, '0.1'), (1000, '1.0'), (1340, '1.3'), (1399, '1.3'), (5400, '5.4'), (99, '0.0')]:
            self.assertEqual(mapas.kilometros_para_envio(metros), km)
        for valor in ('NaN', 'Infinity', '-1', 'texto'):
            with self.assertRaises(ValueError):
                mapas.kilometros_para_envio(valor)

    def test_tarifa_editable_y_minimo_mas_excedente(self):
        self.config.distancia_minima = Decimal('1')
        self.config.costo_minimo_envio = 1000
        for tarifa, esperado in [('100', 1300), ('200', 1600), ('150', 1450)]:
            self.config.tarifa_100m = Decimal(tarifa)
            self.config.save()
            self.assertEqual(calcular_envio('1.3', False), esperado)
        self.assertEqual(calcular_envio('1.3', True), 0)

    def test_busqueda_cacheada_sin_clave_en_respuesta(self):
        payload = {'properties': {'apiKey': 'clave-de-prueba'}, 'features': [{'properties': {
            'formatted': 'Jujuy 87, Resistencia', 'lat': -27.455266, 'lon': -58.992536,
            'result_type': 'building', 'rank': {'match_type': 'full_match'}, 'apiKey': 'clave-de-prueba',
        }}]}
        with mock.patch('pedidos.mapas.urlopen', return_value=self.response(payload)) as remote:
            primero = self.post('buscar', {'texto': 'Jujuy 87, Resistencia'})
            segundo = self.post('buscar', {'texto': 'Jujuy 87, Resistencia'})
        self.assertEqual(primero.status_code, 200)
        self.assertEqual(primero.json(), segundo.json())
        self.assertEqual(remote.call_count, 1)
        self.assertNotContains(primero, 'clave-de-prueba')
        self.assertFalse(primero.json()['resultados'][0]['aproximada'])

    def test_ruta_metrica_origen_del_servidor_y_geometria(self):
        payload = {'features': [{'properties': {'distance': 1340, 'distance_units': 'meters'},
            'geometry': {'type': 'MultiLineString', 'coordinates': [[[-58.992536, -27.455266], [-58.9865, -27.4511]]]}}]}
        with mock.patch('pedidos.mapas.urlopen', return_value=self.response(payload)) as remote:
            response = self.post('recorrido', {'latitud': -27.4511, 'longitud': -58.9865, 'origen': [0, 0]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['distancia_km'], '1.3')
        self.assertEqual(response.json()['distancia_metros'], 1340)
        self.assertIn('units=metric', remote.call_args.args[0].full_url)
        self.assertEqual(response.json()['origen'], [-27.455266, -58.992536])

    def test_no_acepta_millas(self):
        payload = {'features': [{'properties': {'distance': 1.34, 'distance_units': 'Miles'},
            'geometry': {'type': 'MultiLineString', 'coordinates': []}}]}
        with mock.patch('pedidos.mapas.urlopen', return_value=self.response(payload)):
            response = self.post('recorrido', {'latitud': -27.4511, 'longitud': -58.9865})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('distancia_km', response.json())

    def test_falta_clave_y_respuesta_malformada_permiten_manual(self):
        self.config.geoapify_api_key = ''
        self.config.save()
        with mock.patch('pedidos.mapas.urlopen') as remote:
            self.assertEqual(self.post('buscar', {'texto': 'Jujuy 87'}).status_code, 503)
            remote.assert_not_called()
        self.config.geoapify_api_key = 'clave-de-prueba'
        self.config.save()
        with mock.patch('pedidos.mapas.urlopen', return_value=self.response({'features': None})):
            self.assertEqual(self.post('buscar', {'texto': 'Jujuy 87'}).status_code, 503)

    def test_api_timeout_clave_invalida_y_cuota(self):
        for code in (401, 403, 429):
            caches['mapas_control'].clear()
            with mock.patch('pedidos.mapas.urlopen', side_effect=HTTPError('https://example.test', code, 'error', {}, None)):
                response = self.post('buscar', {'texto': 'Jujuy 87'})
                self.assertEqual(response.status_code, 429 if code == 429 else 503)
                self.assertNotContains(response, 'clave-de-prueba', status_code=response.status_code)
        caches['mapas_control'].clear()
        with mock.patch('pedidos.mapas.urlopen', side_effect=URLError('desconectado')):
            self.assertEqual(self.post('buscar', {'texto': 'Jujuy 87'}).status_code, 503)

    @override_settings(MAPAS_LIMITE_DIARIO=1)
    def test_limite_preventivo_no_llama_proveedor(self):
        dia = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        caches['mapas_control'].set('consultas:' + dia, 1)
        with mock.patch('pedidos.mapas.urlopen') as remote:
            self.assertEqual(self.post('buscar', {'texto': 'Jujuy 87'}).status_code, 429)
            remote.assert_not_called()

    def test_post_csrf_y_coordenadas_invalidas(self):
        self.assertEqual(self.client.get('/pedidos/mapas/buscar/').status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        self.assertEqual(csrf_client.post('/pedidos/mapas/buscar/', '{}', content_type='application/json').status_code, 403)
        for lat, lon in [(None, None), (float('nan'), -59), (True, -59), (0, 0)]:
            with mock.patch('pedidos.mapas.urlopen') as remote:
                self.assertEqual(self.post('recorrido', {'latitud': lat, 'longitud': lon}).status_code, 400)
                remote.assert_not_called()
        self.assertEqual(self.post('buscar', {'texto': 'https://maps.google.com'}).status_code, 400)
        self.assertEqual(self.post('buscar', {'texto': 'x' * 301}).status_code, 400)

    def test_clave_no_renderizada_y_conservada_al_cambiar_tarifa(self):
        response = self.client.get('/configuracion/')
        self.assertNotContains(response, 'clave-de-prueba')
        # Usar el formulario directamente para cubrir también instancia no guardada.
        form = ConfiguracionForm(instance=self.config, data={
            'tarifa_100m': '250', 'distancia_minima': '1', 'costo_minimo_envio': '1000',
            'costo_hora_mano_obra': '2500', 'whatsapp_cocina': '', 'geoapify_api_key': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn('clave-de-prueba', str(form['geoapify_api_key']))
        form.save()
        self.config.refresh_from_db()
        self.assertEqual(self.config.geoapify_api_key, 'clave-de-prueba')
        self.assertEqual(self.config.tarifa_100m, 250)
        response = self.client.get('/pedidos/nuevo/')
        self.assertNotContains(response, 'clave-de-prueba')

    def test_coordenadas_nan_no_validas(self):
        form = ConfiguracionForm(data={'tarifa_100m': '100', 'distancia_minima': '1', 'costo_minimo_envio': '1000',
            'costo_hora_mano_obra': '2500', 'local_latitud': 'nan', 'local_longitud': '-58.992536'})
        self.assertFalse(form.is_valid())
        self.assertIn('local_latitud', form.errors)

    def test_mosaicos_cacheados_sin_clave_y_creditos_fraccionados(self):
        z = 14
        x = int((self.config.local_longitud + 180) / 360 * 2 ** z)
        y = int((1 - math.asinh(math.tan(math.radians(self.config.local_latitud))) / math.pi) / 2 * 2 ** z)
        png = b'\x89PNG\r\n\x1a\nprueba'
        remote_response = mock.MagicMock()
        remote_response.__enter__.return_value.read.return_value = png
        url = f'/pedidos/mapas/mosaicos/{z}/{x}/{y}.png'
        with mock.patch('pedidos.mapas.urlopen', return_value=remote_response) as remote:
            first = self.client.get(url)
            second = self.client.get(url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.content, png)
        self.assertEqual(second.content, png)
        self.assertEqual(remote.call_count, 1)
        self.assertEqual(first['Content-Type'], 'image/png')
        self.assertNotIn('clave-de-prueba', first['Cache-Control'])
        dia = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        self.assertEqual(caches['mapas_control'].get('creditos_cuartos:' + dia), 1)
        self.assertEqual(self.client.get(url, HTTP_SEC_FETCH_SITE='cross-site').status_code, 403)

    def test_busqueda_sin_otra_provincia_ni_repetidos_ni_vagos(self):
        """Casos reales de Geoapify: "Av San Martin 2500, Barranqueras" y "Belgrano 800"."""
        def lugar(tipo, nombre, lat, lon, provincia='Chaco'):
            return {'properties': {'result_type': tipo, 'formatted': nombre, 'lat': lat, 'lon': lon, 'state': provincia,
                                   'rank': {'match_type': 'full_match'}}}
        features = [
            lugar('city', 'Barranqueras, CC, Argentina', -27.48299, -58.93579),
            lugar('building', 'Avenida San Martín 2500, Villa Palermo 2', -27.47514, -59.0045),
            lugar('building', 'Avenida San Martín 2500, Villa Centenario', -27.47514, -59.0045),  # mismo punto
            lugar('street', 'Avenida San Martín, Resistencia', -27.45655, -58.98392),
            lugar('building', 'Avenida San Martín 2500, Fontana', -27.41412, -59.01872),
            lugar('building', 'Belgrano 800, Corrientes', -27.47175, -58.84085, provincia='Corrientes'),
        ]
        self.assertEqual([r['direccion'] for r in mapas.limpiar_resultados(features)], [
            'Avenida San Martín 2500, Villa Palermo 2',
            'Avenida San Martín 2500, Fontana',
        ])
        # Si no hay ninguna exacta, se ofrecen las vagas antes que nada.
        vagas = [features[0], features[3]]
        self.assertEqual(len(mapas.limpiar_resultados(vagas)), 2)

    def test_mosaicos_viajan_en_paralelo_respetando_los_turnos(self):
        """
        Antes cada consulta esperaba a la anterior con el cerrojo tomado: 20
        mosaicos de ~1 s bloqueaban las conexiones del navegador y el chequeo
        de estado mostraba "Sistema sin conexion". Ahora viajan a la vez, pero
        separadas por ESPACIO_ENTRE_CONSULTAS.
        """
        png = b'\x89PNG\r\n\x1a\nprueba'
        salidas = []

        def remoto_lento(request, timeout):
            salidas.append(time.monotonic())
            time.sleep(0.5)  # Lo que tarda Geoapify en responder.
            respuesta = mock.MagicMock()
            respuesta.__enter__.return_value.read.return_value = png
            return respuesta

        with mock.patch('pedidos.mapas.urlopen', side_effect=remoto_lento):
            inicio = time.monotonic()
            hilos = [threading.Thread(target=mapas._consultar, args=(f'tile/osm-carto/14/{x}/1.png', {}, 'clave', True))
                     for x in range(4)]
            for hilo in hilos:
                hilo.start()
            for hilo in hilos:
                hilo.join()
            total = time.monotonic() - inicio

        self.assertEqual(len(salidas), 4)
        # En fila hubieran sido 4 x (0.5 + 0.26) = ~3 s.
        self.assertLess(total, 2)
        salidas.sort()
        for anterior, siguiente in zip(salidas, salidas[1:]):
            self.assertGreaterEqual(siguiente - anterior, mapas.ESPACIO_ENTRE_CONSULTAS - 0.02)

    def test_no_consulta_mosaicos_fuera_de_area(self):
        with mock.patch('pedidos.mapas.urlopen') as remote:
            for path in ['/pedidos/mapas/mosaicos/0/0/0.png', '/pedidos/mapas/mosaicos/19/999999/0.png', '/pedidos/mapas/mosaicos/14/0/0.png']:
                self.assertEqual(self.client.get(path).status_code, 400)
            remote.assert_not_called()
