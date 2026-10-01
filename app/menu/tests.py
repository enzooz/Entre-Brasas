from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from config.models import Configuracion
from inventario.models import Ingrediente
from pedidos.models import Pedido, ItemPedido, AdicionalDeItem
from .models import Hamburguesa, Adicional


class ActualizarMenuTests(TestCase):
    def test_reemplazo_preserva_pedidos_stock_y_configuracion_y_es_idempotente(self):
        viejo = Hamburguesa.objects.create(nombre='BBQ', precio=3100, descripcion='Anterior')
        extra_viejo = Adicional.objects.create(nombre='Bacon Extra', precio=500)
        pedido = Pedido.objects.create(cliente_nombre='Histórico', total=3600, estado='entregado')
        item = ItemPedido.objects.create(pedido=pedido, hamburguesa=viejo, cantidad=1, precio_unitario=3100)
        AdicionalDeItem.objects.create(item=item, adicional=extra_viejo, precio=500)
        stock = Ingrediente.objects.create(nombre='Panceta', unidad='kg', stock_actual=7, stock_minimo=1, precio_compra=1234)
        config = Configuracion.objects.create(pk=1, tarifa_100m=123, whatsapp_cocina='54912345678')
        Hamburguesa.objects.create(nombre='Cheese', precio=1, descripcion='Vieja', activa=False)
        for _ in range(2):
            call_command('seed_data', reemplazar_menu=True, stdout=StringIO())
        viejo.refresh_from_db()
        extra_viejo.refresh_from_db()
        stock.refresh_from_db()
        config.refresh_from_db()
        pedido.refresh_from_db()
        self.assertFalse(viejo.activa)
        self.assertFalse(extra_viejo.activo)
        self.assertEqual(pedido.total, 3600)
        self.assertEqual(pedido.items.get().precio_unitario, 3100)
        self.assertEqual(pedido.items.get().adicionales.get().precio, 500)
        self.assertEqual(stock.stock_actual, 7)
        self.assertEqual(stock.precio_compra, 1234)
        self.assertEqual(config.tarifa_100m, 123)
        self.assertEqual(config.whatsapp_cocina, '54912345678')
        esperados = {'Sagrada': 16500, 'Full': 15500, 'La Pepi': 14000, 'Crispy': 13500, 'Freskita': 11500, 'Baconera': 13500, 'Tradi': 11500, 'Cheese': 10500}
        self.assertEqual(dict(Hamburguesa.objects.filter(activa=True).values_list('nombre', 'precio')), esperados)
        self.assertEqual(Adicional.objects.filter(activo=True).count(), 5)
        for adicional in Adicional.objects.filter(activo=True):
            self.assertEqual(adicional.hamburguesas.filter(activa=True).count(), 8)


class MenuActivoTests(TestCase):
    def setUp(self):
        self.activa = Hamburguesa.objects.create(nombre='Cheese', precio=10500, descripcion='Actual')
        self.inactiva = Hamburguesa.objects.create(nombre='BBQ anterior', precio=3100, descripcion='Anterior', activa=False)
        self.extra = Adicional.objects.create(nombre='Panceta', precio=2000)
        self.extra.hamburguesas.add(self.activa, self.inactiva)
        self.viejo = Adicional.objects.create(nombre='Bacon anterior', precio=500, activo=False)

    def test_hamburguesas_oculta_inactivas_sin_borrarlas(self):
        response = self.client.get(reverse('menu:listar_hamburguesas'))
        self.assertContains(response, 'Cheese')
        self.assertNotContains(response, 'BBQ anterior')
        self.assertTrue(Hamburguesa.objects.filter(pk=self.inactiva.pk).exists())

    def test_adicionales_oculta_inactivos_y_vinculos_a_hamburguesas_inactivas(self):
        response = self.client.get(reverse('menu:listar_adicionales'))
        self.assertContains(response, 'Panceta')
        self.assertContains(response, 'Cheese')
        self.assertNotContains(response, 'Bacon anterior')
        self.assertNotContains(response, 'BBQ anterior')
        self.assertTrue(Adicional.objects.filter(pk=self.viejo.pk).exists())

    def test_desactivar_hamburguesa_la_retira_del_listado(self):
        self.client.get(reverse('menu:activar_hamburguesa', args=[self.activa.pk]))
        response = self.client.get(reverse('menu:listar_hamburguesas'))
        self.assertNotContains(response, 'Cheese')
        self.assertContains(response, 'No hay hamburguesas activas')

    def test_desactivar_adicional_lo_retira_del_listado(self):
        self.client.get(reverse('menu:activar_adicional', args=[self.extra.pk]))
        response = self.client.get(reverse('menu:listar_adicionales'))
        self.assertNotContains(response, 'Panceta')
        self.assertContains(response, 'No hay adicionales activos')
