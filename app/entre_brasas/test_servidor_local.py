import http.client
from contextlib import closing
import os
from pathlib import Path
import re
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from unittest import mock, skipUnless

from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from . import servidor_local


class ApagadoWebTests(SimpleTestCase):
    def setUp(self):
        self.evento = threading.Event()
        servidor_local.registrar(self.evento)

    def tearDown(self):
        servidor_local.registrar(None)

    def test_get_solo_confirma_y_no_apaga(self):
        response = self.client.get(reverse('apagar_sistema'))
        self.assertContains(response, 'Sí, apagar sistema')
        self.assertContains(response, 'formularios sin guardar')
        self.assertFalse(self.evento.is_set())
        self.assertTrue(servidor_local.disponible())

    def test_post_sin_csrf_no_apaga(self):
        cliente = Client(enforce_csrf_checks=True)
        response = cliente.post(reverse('apagar_sistema'))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(servidor_local.disponible())

    def test_post_valido_entrega_confirmacion_y_solicita_cierre(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.get(reverse('apagar_sistema'))
        with mock.patch('entre_brasas.servidor_local.threading.Timer') as timer:
            response = cliente.post(reverse('apagar_sistema'), {'csrfmiddlewaretoken': cliente.cookies['csrftoken'].value})
        self.assertContains(response, 'Ya podés cerrar esta pestaña')
        timer.assert_called_once_with(1, self.evento.set)
        timer.return_value.start.assert_called_once()
        self.assertFalse(servidor_local.disponible())

    def test_no_se_apaga_desde_otra_computadora(self):
        response = self.client.post(reverse('apagar_sistema'), REMOTE_ADDR='192.168.1.25')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(servidor_local.disponible())

    def test_no_hay_control_para_runserver(self):
        servidor_local.registrar(None)
        response = self.client.get(reverse('apagar_sistema'))
        self.assertEqual(response.status_code, 409)
        self.assertNotContains(response, 'Sí, apagar sistema', status_code=409)

    def test_solicitudes_duplicadas_no_programan_dos_apagados(self):
        with mock.patch('entre_brasas.servidor_local.threading.Timer') as timer:
            self.assertTrue(servidor_local.solicitar_apagado())
            self.assertFalse(servidor_local.solicitar_apagado())
        self.assertEqual(timer.call_count, 1)

    def test_estado_no_se_cachea_y_distingue_el_apagado(self):
        response = self.client.get(reverse('estado_sistema'))
        self.assertFalse(response.json()['apagando'])
        self.assertIn('no-store', response['Cache-Control'])
        instancia = response.json()['instancia']
        with mock.patch('entre_brasas.servidor_local.threading.Timer'):
            servidor_local.solicitar_apagado()
        response = self.client.get(reverse('estado_sistema'))
        self.assertTrue(response.json()['apagando'])
        self.assertEqual(response.json()['instancia'], instancia)

    def test_pantalla_de_despedida_ya_se_entrega_bloqueada(self):
        with mock.patch('entre_brasas.servidor_local.threading.Timer'):
            response = self.client.post(reverse('apagar_sistema'))
        self.assertContains(response, 'class="system-off" data-system-off="true"')
        self.assertContains(response, 'aria-label="Navegación principal" inert')
        self.assertContains(response, '<main class="app-main" inert>')
        self.assertContains(response, 'js/estado-sistema.js')


class CambiosBloqueadosTests(TestCase):
    def setUp(self):
        servidor_local.registrar(threading.Event())
        with mock.patch('entre_brasas.servidor_local.threading.Timer'):
            servidor_local.solicitar_apagado()

    def tearDown(self):
        servidor_local.registrar(None)

    def test_no_se_guardan_pedidos_ni_configuracion_durante_el_apagado(self):
        from config.models import Configuracion
        from pedidos.models import Pedido
        config = Configuracion.objects.create()
        anterior = config.tarifa_100m
        for ruta in ('pedidos:crear_pedido', 'config:panel_config', 'inventario:registrar_movimiento', 'menu:crear_hamburguesa'):
            with self.subTest(ruta=ruta):
                response = self.client.post(reverse(ruta), {'tarifa_100m': '9999', 'cliente_nombre': 'No guardar'})
                self.assertEqual(response.status_code, 503)
                self.assertTrue(response.json()['apagando'])
        config.refresh_from_db()
        self.assertEqual(config.tarifa_100m, anterior)
        self.assertFalse(Pedido.objects.exists())

    def test_tambien_se_bloquean_las_acciones_antiguas_que_usan_get(self):
        from menu.models import Hamburguesa
        from inventario.models import Ingrediente, Receta
        from pedidos.models import Pedido
        burger = Hamburguesa.objects.create(nombre='No desactivar', precio=1000)
        ingrediente = Ingrediente.objects.create(nombre='No tocar', unidad='unidades', stock_minimo=0)
        receta = Receta.objects.create(hamburguesa=burger, ingrediente=ingrediente, cantidad_requerida=1)
        pedido = Pedido.objects.create(cliente_nombre='No avanzar', total=1000)
        for url in (reverse('menu:activar_hamburguesa', args=[burger.pk]),
                    reverse('pedidos:avanzar_pedido', args=[pedido.pk]),
                    reverse('inventario:borrar_de_receta', args=[receta.pk])):
            self.assertEqual(self.client.get(url).status_code, 503)
        burger.refresh_from_db()
        pedido.refresh_from_db()
        self.assertTrue(burger.activa)
        self.assertEqual(pedido.estado, 'pendiente')
        self.assertTrue(Receta.objects.filter(pk=receta.pk).exists())

    def test_todas_las_pantallas_se_entregan_en_gris_al_cerrar(self):
        for ruta in ('inicio', 'pedidos:crear_pedido', 'pedidos:cola_pedidos', 'pedidos:historial_pedidos',
                     'menu:listar_hamburguesas', 'menu:listar_adicionales', 'inventario:ver_inventario',
                     'inventario:listar_ingredientes', 'inventario:ver_recetas', 'reportes:reportes_ventas',
                     'costos:ver_costos', 'config:panel_config'):
            with self.subTest(ruta=ruta):
                response = self.client.get(reverse(ruta))
                self.assertContains(response, 'data-system-off="true"', status_code=503)
                self.assertContains(response, 'Esta pantalla no admite cambios', status_code=503)


@skipUnless(sys.platform == 'win32', 'El iniciador del cliente usa pythonw y bloqueo de Windows')
class IniciadorWindowsTests(SimpleTestCase):
    def test_pythonw_arranca_no_duplica_apaga_y_reabre_sin_perder_datos(self):
        app = Path(__file__).resolve().parents[1]
        ejecutable = app / 'venv' / 'Scripts' / 'pythonw.exe'
        with tempfile.TemporaryDirectory(prefix='entre-brasas-servidor-') as temporal:
            env = os.environ.copy()
            env['LOCALAPPDATA'] = temporal
            env['ENTRE_BRASAS_PRODUCCION'] = '1'
            env['DJANGO_SETTINGS_MODULE'] = 'entre_brasas.settings_pruebas_servidor'
            env.pop('PYTHONPATH', None)
            registro = Path(temporal) / 'EntreBrasas' / 'servidor.log'
            procesos = []
            conexion = None
            try:
                proceso = subprocess.Popen([str(ejecutable), 'iniciar.py', '--sin-navegador', '--puerto', '0'], cwd=app, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
                procesos.append(proceso)
                limite = time.monotonic() + 15
                coincidencia = None
                while time.monotonic() < limite and proceso.poll() is None:
                    if registro.exists():
                        coincidencia = re.search(r'disponible en http://127.0.0.1:(\d+)', registro.read_text(encoding='utf-8'))
                        if coincidencia:
                            break
                    time.sleep(0.1)
                self.assertIsNotNone(coincidencia, registro.read_text(encoding='utf-8') if registro.exists() else 'No abrió el registro')
                puerto = int(coincidencia.group(1))

                # Una segunda apertura no inicia otro servidor ni apaga el actual.
                duplicado = subprocess.Popen([str(ejecutable), 'iniciar.py', '--sin-navegador', '--puerto', str(puerto)], cwd=app, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
                procesos.append(duplicado)
                self.assertEqual(duplicado.wait(timeout=5), 0)
                self.assertIsNone(proceso.poll())

                conexion = http.client.HTTPConnection('127.0.0.1', puerto, timeout=5)
                conexion.request('GET', '/')
                response = conexion.getresponse()
                self.assertEqual(response.status, 200)
                self.assertIn('Apagar sistema', response.read().decode())
                conexion.request('POST', '/sistema/apagar/')
                response = conexion.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
                self.assertIsNone(proceso.poll())

                # Guardamos un pedido de prueba en la base AISLADA, no la del usuario.
                crear = "from pedidos.models import Pedido; Pedido.objects.create(cliente_nombre='Conservar al apagar',total=12345)"
                subprocess.run([str(app / 'venv' / 'Scripts' / 'python.exe'), 'manage.py', 'shell', '-c', crear], cwd=app, env=env, check=True, capture_output=True)

                def apagar():
                    conexion.request('GET', '/sistema/apagar/')
                    response = conexion.getresponse()
                    html = response.read().decode()
                    self.assertEqual(response.status, 200)
                    token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html).group(1)
                    cookie = response.getheader('Set-Cookie').split(';', 1)[0]
                    conexion.request('POST', '/sistema/apagar/', 'csrfmiddlewaretoken=' + token, headers={'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookie})
                    response = conexion.getresponse()
                    self.assertEqual(response.status, 200)
                    self.assertIn('Ya podés cerrar esta pestaña', response.read().decode())
                    conexion.close()

                apagar()
                self.assertEqual(proceso.wait(timeout=10), 0)
                with socket.socket() as prueba:
                    self.assertNotEqual(prueba.connect_ex(('127.0.0.1', puerto)), 0)
                with closing(sqlite3.connect(Path(temporal) / 'EntreBrasas' / 'db.sqlite3')) as base:
                    self.assertEqual(base.execute('SELECT total FROM pedidos_pedido').fetchall(), [(12345,)])

                reinicio = subprocess.Popen([str(ejecutable), 'iniciar.py', '--sin-navegador', '--puerto', str(puerto)], cwd=app, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
                procesos.append(reinicio)
                limite = time.monotonic() + 10
                while time.monotonic() < limite:
                    with socket.socket() as prueba:
                        if prueba.connect_ex(('127.0.0.1', puerto)) == 0:
                            break
                    time.sleep(0.1)
                conexion = http.client.HTTPConnection('127.0.0.1', puerto, timeout=5)
                conexion.request('GET', '/')
                response = conexion.getresponse()
                self.assertEqual(response.status, 200)
                self.assertIn('Conservar al apagar', response.read().decode())
                apagar()
                self.assertEqual(reinicio.wait(timeout=10), 0)
            finally:
                if conexion:
                    conexion.close()
                # Solo procesos de prueba creados aquí, nunca servidores del usuario.
                for proceso in procesos:
                    if proceso.poll() is None:
                        proceso.terminate()
                        proceso.wait(timeout=5)
