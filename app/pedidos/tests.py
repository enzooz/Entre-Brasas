from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from config.models import Configuracion
from menu.models import Adicional, Hamburguesa
from .calculos import calcular_envio, descontar_stock
from .comanda import armar_comanda
from .models import Pedido
from inventario.models import Ingrediente, Receta


class EnvioTests(TestCase):
    def setUp(self):
        self.config = Configuracion.objects.create(
            pk=1, tarifa_100m=100, distancia_minima=0, costo_minimo_envio=0,
        )

    def test_distancias_exactas_no_redondeadas_a_kilometros(self):
        for distancia, costo in [('0.1', 100), ('5.4', 5400), ('5,4', 5400), ('5.45', 5450), ('0', 0)]:
            with self.subTest(distancia=distancia):
                self.assertEqual(calcular_envio(distancia, False), costo)

    def test_retiro_no_cobra(self):
        self.assertEqual(calcular_envio('5.4', True), 0)

    def test_minimo_cubre_el_tramo_incluido(self):
        self.config.distancia_minima = Decimal('0.1')
        self.config.costo_minimo_envio = 1000
        self.config.save()
        self.assertEqual(calcular_envio('0.09', False), 1000)
        self.assertEqual(calcular_envio('0.1', False), 1000)
        self.assertEqual(calcular_envio('5.4', False), 6300)
        self.assertEqual(calcular_envio('5.4', True), 0)

    def test_minimo_mas_solo_la_distancia_excedente(self):
        self.config.distancia_minima = Decimal('1')
        self.config.costo_minimo_envio = 1000
        self.config.tarifa_100m = Decimal('50')
        self.config.save()
        self.assertEqual(calcular_envio('0.99', False), 1000)
        self.assertEqual(calcular_envio('1', False), 1000)
        self.assertEqual(calcular_envio('5,4', False), 3200)
        self.assertEqual(calcular_envio('5.45', False), 3225)

    def test_ejemplo_del_local_y_limites_del_tramo(self):
        self.config.distancia_minima = Decimal('1')
        self.config.costo_minimo_envio = 1000
        self.config.save()
        for distancia, costo in [('0', 1000), ('0.1', 1000), ('0.9', 1000),
                                 ('1', 1000), ('1.1', 1100), ('1,3', 1300), ('5.4', 5400)]:
            with self.subTest(distancia=distancia):
                self.assertEqual(calcular_envio(distancia, False), costo)

    def test_valores_arbitrarios_no_asumen_un_kilometro_incluido(self):
        self.config.distancia_minima = Decimal('2.3')
        self.config.costo_minimo_envio = 700
        self.config.tarifa_100m = 80
        self.config.save()
        self.assertEqual(calcular_envio('2.3', False), 700)
        self.assertEqual(calcular_envio('2.7', False), 1020)

    def test_base_y_tarifa_decimal_se_redondean_una_sola_vez(self):
        self.config.costo_minimo_envio = 1000
        self.config.tarifa_100m = Decimal('55.05')
        self.config.save()
        self.assertEqual(calcular_envio('1', False), 1551)

    def test_redondea_solo_pesos_igual_que_el_navegador(self):
        self.config.tarifa_100m = Decimal('55.05')
        self.config.save()
        self.assertEqual(calcular_envio('1', False), 551)

    def test_datos_formulario_usan_tarifa_nueva(self):
        response = self.client.get(reverse('pedidos:crear_pedido'))
        self.assertEqual(Decimal(response.context['datos_formulario']['tarifa_100m']), Decimal('100'))
        self.assertContains(response, '5,4 km son 5 km y 400 metros')


class UnidadesPedidoTests(TestCase):
    def setUp(self):
        self.burger = Hamburguesa.objects.create(nombre='Baconera', descripcion='Dos medallones', precio=13500)
        self.extra = Adicional.objects.create(nombre='Panceta', precio=2000)
        self.extra.hamburguesas.add(self.burger)
        self.medallon = Adicional.objects.create(nombre='Medallón extra', precio=2500, es_medallon_extra=True)
        self.medallon.hamburguesas.add(self.burger)
        self.datos = {
            'cliente_nombre': 'Prueba', 'retiro_local': 'true', 'metodo_pago': 'efectivo',
            'filas[]': ['0', '1'],
            'hamburguesa_0': str(self.burger.pk), 'cantidad_0': '1', 'nota_0': 'Sin cebolla',
            'adicionales_0[]': [str(self.extra.pk)],
            'hamburguesa_1': str(self.burger.pk), 'cantidad_1': '1', 'nota_1': 'Bien cocida',
        }

    def crear(self, **cambios):
        return self.client.post(reverse('pedidos:crear_pedido'), {**self.datos, **cambios})

    def test_no_hay_boton_agregar_otra(self):
        response = self.client.get(reverse('pedidos:crear_pedido'))
        self.assertNotContains(response, 'Agregar otra')
        self.assertNotContains(response, 'agregarOtra')
        self.assertContains(response, 'Cada toque agrega una hamburguesa')

    def test_borrador_se_confirma_solo_despues_de_crear_el_pedido(self):
        token = '75c33a01-fb02-4c8f-8103-ffea8f13be01'
        response = self.crear(borrador_token=token)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Pedido.objects.exists())
        cookie = response.cookies['eb_pedido_creado_' + token.replace('-', '')]
        self.assertEqual(cookie.value, '1')
        self.assertEqual(cookie['samesite'], 'Strict')

    def test_error_al_crear_no_confirma_ni_borra_el_borrador(self):
        response = self.crear(borrador_token='75c33a01-fb02-4c8f-8103-ffea8f13be01', cliente_nombre='')
        self.assertFalse(Pedido.objects.exists())
        self.assertFalse(any(name.startswith('eb_pedido_creado_') for name in response.cookies))

    def test_token_invalido_no_crea_cookies_arbitrarias(self):
        response = self.crear(borrador_token='malicioso; token')
        self.assertTrue(Pedido.objects.exists())
        self.assertFalse(any(name.startswith('eb_pedido_creado_') for name in response.cookies))

    def test_misma_hamburguesa_con_extras_y_notas_independientes(self):
        self.crear()
        pedido = Pedido.objects.get()
        items = list(pedido.items.order_by('pk'))
        self.assertEqual([i.cantidad for i in items], [1, 1])
        self.assertEqual([i.nota for i in items], ['Sin cebolla', 'Bien cocida'])
        self.assertEqual(items[0].adicionales.count(), 1)
        self.assertEqual(items[1].adicionales.count(), 0)
        self.assertEqual(pedido.total, 29000)
        comanda = armar_comanda(pedido)
        self.assertIn('1 Baconera + Panceta\n   Nota: Sin cebolla\n1 Baconera\n   Nota: Bien cocida', comanda)

    def test_medallon_se_cobra_solo_en_su_unidad(self):
        self.crear(medallones_1='1')
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.total, 31500)
        self.assertIn('1 Baconera + 1 medallón extra', armar_comanda(pedido))

    def test_cantidad_de_cliente_anterior_tambien_se_separa(self):
        self.crear(**{'filas[]': ['1'], 'cantidad_1': '2'})
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.items.count(), 2)
        self.assertEqual(pedido.total, 27000)
        self.assertTrue(all(i.cantidad == 1 for i in pedido.items.all()))

    def test_stock_extra_se_descuenta_una_vez_y_no_bloquea(self):
        carne = Ingrediente.objects.create(nombre='Carne', unidad='unidades', stock_minimo=1, stock_actual=0)
        panceta = Ingrediente.objects.create(nombre='Panceta', unidad='kg', stock_minimo=1, stock_actual=1)
        Receta.objects.create(hamburguesa=self.burger, ingrediente=carne, cantidad_requerida=2)
        Receta.objects.create(adicional=self.extra, ingrediente=panceta, cantidad_requerida=Decimal('0.04'))
        self.crear()
        descontar_stock(Pedido.objects.get())
        carne.refresh_from_db()
        panceta.refresh_from_db()
        self.assertEqual(carne.stock_actual, -4)
        self.assertEqual(panceta.stock_actual, Decimal('0.96'))

    def test_envio_post_usa_distancia_decimal_incluida_coma(self):
        Configuracion.objects.create(pk=1, tarifa_100m=100, distancia_minima=0, costo_minimo_envio=0)
        self.crear(retiro_local='false', distancia_km='5,4', cliente_direccion='Jujuy 87', cliente_telefono='12345678')
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.distancia_km, Decimal('5.4'))
        self.assertEqual(pedido.costo_envio, 5400)
        self.assertEqual(pedido.total, 34400)

    def test_envio_guardado_y_total_incluyen_la_base_una_sola_vez(self):
        Configuracion.objects.create(pk=1, tarifa_100m=50, distancia_minima=1, costo_minimo_envio=1000)
        self.crear(retiro_local='false', distancia_km='5,4', cliente_direccion='Jujuy 87', cliente_telefono='12345678')
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.costo_envio, 3200)
        self.assertEqual(pedido.total, 32200)
        self.assertIn('Total $32.200', armar_comanda(pedido))

    def test_cambio_de_tarifa_no_recalcula_pedidos_historicos(self):
        config = Configuracion.objects.create(pk=1, tarifa_100m=50, distancia_minima=1, costo_minimo_envio=1000)
        self.crear(retiro_local='false', distancia_km='5.4', cliente_direccion='Prueba', cliente_telefono='12345678')
        pedido = Pedido.objects.get()
        Pedido.objects.filter(pk=pedido.pk).update(costo_envio=3700, total=32700)
        config.tarifa_100m = 100
        config.save()
        self.assertEqual(calcular_envio('5.4', False), 5400)
        pedido.refresh_from_db()
        self.assertEqual(pedido.costo_envio, 3700)
        self.assertEqual(pedido.total, 32700)

    def test_distancia_invalida_no_guarda_pedido(self):
        for distancia in ['', 'NaN', 'Infinity', '-1', '1000', '999.91', '5.45', '5,45', '5.456', 'abc']:
            with self.subTest(distancia=distancia):
                self.crear(retiro_local='false', distancia_km=distancia, cliente_direccion='Jujuy 87', cliente_telefono='12345678')
                self.assertFalse(Pedido.objects.exists())

    def test_formulario_pide_distancia_con_un_solo_decimal(self):
        response = self.client.get(reverse('pedidos:crear_pedido'))
        self.assertContains(response, 'max="999.9" step="0.1"')
        self.assertContains(response, 'Usá como máximo un decimal')

    def test_producto_inactivo_no_se_vende(self):
        self.burger.activa = False
        self.burger.save()
        self.crear()
        self.assertFalse(Pedido.objects.exists())

    def test_extra_no_permitido_no_se_guarda(self):
        self.extra.hamburguesas.clear()
        self.crear()
        self.assertFalse(Pedido.objects.exists())

    def test_cantidad_invalida_no_se_guarda(self):
        for cantidad in ['0', '-1', 'NaN', '101']:
            self.crear(cantidad_0=cantidad)
            self.assertFalse(Pedido.objects.exists())

    def test_whatsapp_reconoce_menu_y_extras_nuevos(self):
        response = self.client.post(reverse('pedidos:interpretar_mensaje'), {'mensaje': 'Prueba\n1 baconera con panceta extra\n1 baconera sin cebolla\nRetira'})
        datos = response.json()
        self.assertEqual(len(datos['items']), 2)
        self.assertEqual(datos['items'][0]['adicionales'], [self.extra.pk])
        self.assertEqual(datos['items'][1]['adicionales'], [])
