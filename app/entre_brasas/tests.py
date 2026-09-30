from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from inventario.models import Ingrediente, Receta
from menu.models import Hamburguesa
from pedidos.models import Pedido


class InicioTests(TestCase):
    def test_inicio_vacio_ofrece_siguiente_paso(self):
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['resumen']['total'], 0)
        self.assertEqual(response.context['ventas_hoy'], 0)
        self.assertContains(response, 'Tomar un pedido')
        self.assertContains(response, 'Todo al día por acá.')

    def test_resumen_respeta_estados_fecha_y_stock_activo(self):
        for estado in ['pendiente', 'en_preparacion', 'en_camino', 'cancelado']:
            Pedido.objects.create(cliente_nombre=estado, estado=estado, metodo_pago='efectivo', total=1000)
        Pedido.objects.create(cliente_nombre='Entregado hoy', estado='entregado', metodo_pago='efectivo', total=2500)
        viejo = Pedido.objects.create(cliente_nombre='Ayer', estado='entregado', metodo_pago='efectivo', total=9000)
        Pedido.objects.filter(pk=viejo.pk).update(fecha_creacion=timezone.now() - timedelta(days=2))
        pan = Ingrediente.objects.create(nombre='Pan', unidad='unidades', stock_actual=1, stock_minimo=5)
        burger = Hamburguesa.objects.create(nombre='Activa', precio=2500, descripcion='Prueba')
        Receta.objects.create(hamburguesa=burger, ingrediente=pan, cantidad_requerida=1)
        Ingrediente.objects.create(nombre='Inactivo', unidad='kg', stock_actual=0, stock_minimo=5, activo=False)
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.context['resumen'], {'total': 3, 'pendientes': 1, 'preparando': 1, 'en_camino': 1})
        self.assertEqual(response.context['ventas_hoy'], 2500)
        self.assertEqual(response.context['entregados_hoy'], 1)
        self.assertEqual(response.context['faltantes_count'], 1)

    def test_rutas_principales_comparten_navegacion(self):
        for ruta in ['pedidos:crear_pedido', 'pedidos:cola_pedidos', 'pedidos:historial_pedidos',
                     'menu:listar_hamburguesas', 'menu:listar_adicionales', 'inventario:ver_inventario',
                     'inventario:listar_ingredientes', 'inventario:ver_recetas', 'inventario:registrar_movimiento',
                     'reportes:reportes_ventas', 'costos:ver_costos', 'config:panel_config']:
            with self.subTest(ruta=ruta):
                response = self.client.get(reverse(ruta))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'aria-current="page"', count=1)
                self.assertContains(response, 'css/sistema.css')

    def test_creacion_de_pedido_conserva_comanda_y_total(self):
        hamburguesa = Hamburguesa.objects.create(nombre='Clásica', descripcion='De prueba', precio=2500)
        response = self.client.post(reverse('pedidos:crear_pedido'), {
            'cliente_nombre': 'Prueba', 'retiro_local': 'true', 'metodo_pago': 'efectivo',
            'filas[]': ['0'], 'hamburguesa_0': str(hamburguesa.pk), 'cantidad_0': '2', 'nota_0': 'Sin cebolla',
        })
        pedido = Pedido.objects.get()
        self.assertRedirects(response, reverse('pedidos:detalle_pedido', args=[pedido.pk]))
        self.assertEqual(pedido.total, 5000)
        self.assertEqual(pedido.estado, 'pendiente')
        self.assertContains(self.client.get(response.url), 'Sin cebolla')
