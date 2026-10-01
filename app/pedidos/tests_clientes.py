from importlib import import_module
from types import SimpleNamespace
from unittest import mock

from django.apps import apps
from django.db import connection
from django.test import TestCase
from django.urls import reverse

from menu.models import Hamburguesa
from .clientes import normalizar_telefono
from .models import Cliente, Pedido


class ClientesTests(TestCase):
    def setUp(self):
        self.burger = Hamburguesa.objects.create(nombre='Cheese', precio=10500, descripcion='Prueba')
        self.datos = {'cliente_nombre': 'Agostina', 'cliente_telefono': '+54 9 362 123-4567',
                      'cliente_direccion': 'Dirección de prueba', 'retiro_local': 'true',
                      'metodo_pago': 'efectivo', 'filas[]': ['0'], 'hamburguesa_0': str(self.burger.pk)}

    def crear(self, **cambios):
        return self.client.post(reverse('pedidos:crear_pedido'), {**self.datos, **cambios})

    def test_crear_guarda_cliente_y_copia_historica(self):
        self.crear()
        cliente = Cliente.objects.get()
        pedido = Pedido.objects.get()
        self.assertEqual(cliente.telefono_clave, '5493621234567')
        self.assertEqual(pedido.cliente_id, cliente.pk)
        self.assertEqual(pedido.cliente_nombre, 'Agostina')

    def test_telefono_equivalente_no_duplica_ni_cambia_pedidos_viejos(self):
        self.crear()
        primero = Pedido.objects.get()
        self.crear(cliente_nombre='Agostina actualizada', cliente_telefono='5493621234567', cliente_direccion='Otra dirección')
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Cliente.objects.get().direccion, 'Otra dirección')
        primero.refresh_from_db()
        self.assertEqual(primero.cliente_nombre, 'Agostina')
        self.assertEqual(primero.cliente_direccion, 'Dirección de prueba')
        self.assertEqual(primero.total, 10500)

    def test_retiro_sin_direccion_no_borra_direccion_guardada(self):
        self.crear()
        self.crear(cliente_direccion='')
        self.assertEqual(Cliente.objects.get().direccion, 'Dirección de prueba')

    def test_homonimos_con_otros_telefonos_no_se_unen(self):
        self.crear()
        self.crear(cliente_telefono='3627654321')
        self.assertEqual(Cliente.objects.count(), 2)

    def test_sin_telefono_no_fusiona_por_nombre_y_permite_elegir_existente(self):
        self.crear(cliente_telefono='')
        cliente = Cliente.objects.get()
        self.crear(cliente_telefono='')
        self.assertEqual(Cliente.objects.count(), 2)
        self.crear(cliente_telefono='', cliente_id=str(cliente.pk))
        self.assertEqual(Cliente.objects.count(), 2)
        self.assertEqual(Pedido.objects.latest('pk').cliente_id, cliente.pk)

    def test_cambiar_telefono_del_elegido_no_reasigna_sus_pedidos(self):
        self.crear()
        primero = Pedido.objects.get()
        self.crear(cliente_id=str(primero.cliente_id), cliente_telefono='3627654321')
        ultimo = Pedido.objects.latest('pk')
        self.assertNotEqual(primero.cliente_id, ultimo.cliente_id)

    def test_error_no_guarda_cliente_ni_pedido(self):
        for datos in [{'cliente_nombre': ''}, {'cliente_telefono': 'abc1234567'},
                      {'cliente_id': 'incorrecto'}, {'cliente_id': '999'}, {'cliente_nombre': 'x' * 201}]:
            with self.subTest(datos=datos):
                self.crear(**datos)
                self.assertFalse(Cliente.objects.exists())
                self.assertFalse(Pedido.objects.exists())

    def test_error_interno_revierte_cliente_y_pedido(self):
        with mock.patch('pedidos.views.crear_items_del_pedido', side_effect=RuntimeError('Error de prueba')):
            with self.assertRaises(RuntimeError):
                self.crear()
        self.assertFalse(Cliente.objects.exists())
        self.assertFalse(Pedido.objects.exists())

    def test_busca_nombre_o_telefono_sin_guardar_y_sin_cache(self):
        self.crear()
        ruta = reverse('pedidos:buscar_clientes')
        for consulta in ['agostina', '362 123', '+54 9 362']:
            response = self.client.get(ruta, {'q': consulta})
            self.assertEqual(len(response.json()['clientes']), 1)
            self.assertIn('no-store', response['Cache-Control'])
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(self.client.post(ruta).status_code, 405)

    def test_consulta_corta_vacia_y_sin_resultados(self):
        for consulta in ['', 'a', 'inexistente']:
            self.assertEqual(self.client.get(reverse('pedidos:buscar_clientes'), {'q': consulta}).json(), {'clientes': []})

    def test_resultados_acotados(self):
        for i in range(12):
            Cliente.objects.create(nombre=f'Prueba {i}')
        self.assertEqual(len(self.client.get(reverse('pedidos:buscar_clientes'), {'q': 'Prueba'}).json()['clientes']), 8)

    def test_no_adivina_paises_ni_prefijos(self):
        self.assertEqual(normalizar_telefono('(362) 123-4567'), '3621234567')
        self.assertNotEqual(normalizar_telefono('+54 9 362 1234567'), normalizar_telefono('3621234567'))
        self.assertIsNone(normalizar_telefono('123'))


class ImportarClientesTests(TestCase):
    def test_migracion_agrupa_telefonos_y_preserva_todos_los_datos_historicos(self):
        primero = Pedido.objects.create(cliente_nombre='Nombre viejo', cliente_telefono='+54 9 362 1234567', cliente_direccion='Dirección vieja', total=12345)
        segundo = Pedido.objects.create(cliente_nombre='Nombre nuevo', cliente_telefono='5493621234567', cliente_direccion='', total=45678)
        sin_telefono = Pedido.objects.create(cliente_nombre='Nombre nuevo', cliente_telefono='', total=999)
        antes = list(Pedido.objects.values('id', 'cliente_nombre', 'cliente_telefono', 'cliente_direccion', 'total', 'fecha_creacion', 'estado'))
        migracion = import_module('pedidos.migrations.0005_importar_clientes')
        editor = SimpleNamespace(connection=connection)
        migracion.importar_clientes(apps, editor)
        migracion.importar_clientes(apps, editor)
        self.assertEqual(Cliente.objects.count(), 1)
        cliente = Cliente.objects.get()
        self.assertEqual(cliente.nombre, 'Nombre nuevo')
        self.assertEqual(cliente.direccion, 'Dirección vieja')
        self.assertEqual(list(Pedido.objects.values('id', 'cliente_nombre', 'cliente_telefono', 'cliente_direccion', 'total', 'fecha_creacion', 'estado')), antes)
        self.assertEqual(list(Pedido.objects.filter(pk__in=[primero.pk, segundo.pk]).values_list('cliente_id', flat=True)), [cliente.pk, cliente.pk])
        sin_telefono.refresh_from_db()
        self.assertIsNone(sin_telefono.cliente_id)
