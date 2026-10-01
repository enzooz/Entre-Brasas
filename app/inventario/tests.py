from django.test import TestCase
from django.urls import reverse

from menu.models import Hamburguesa, Adicional
from .models import Ingrediente, Receta, ingredientes_del_menu_activo
from .forms import MovimientoForm


class InventarioMenuActivoTests(TestCase):
    def setUp(self):
        self.burger = Hamburguesa.objects.create(nombre='Cheese', precio=10500, descripcion='Actual')
        self.vieja = Hamburguesa.objects.create(nombre='BBQ', precio=3100, descripcion='Vieja', activa=False)
        self.pan = Ingrediente.objects.create(nombre='Pan actual', unidad='unidades', stock_actual=0, stock_minimo=5)
        self.viejo = Ingrediente.objects.create(nombre='Salsa vieja', unidad='L', stock_actual=0, stock_minimo=5)
        self.sin_receta = Ingrediente.objects.create(nombre='Sin uso', unidad='kg', stock_actual=0, stock_minimo=5)
        Receta.objects.create(hamburguesa=self.burger, ingrediente=self.pan, cantidad_requerida=1)
        Receta.objects.create(hamburguesa=self.vieja, ingrediente=self.pan, cantidad_requerida=1)
        Receta.objects.create(hamburguesa=self.vieja, ingrediente=self.viejo, cantidad_requerida=1)

    def test_tabla_y_avisos_solo_contienen_ingredientes_del_menu_activo(self):
        response = self.client.get(reverse('inventario:ver_inventario'))
        self.assertEqual(list(response.context['ingredientes']), [self.pan])
        self.assertEqual(response.context['sin_contar'], [self.pan])
        self.assertNotContains(response, 'Salsa vieja')
        self.assertNotContains(response, 'Sin uso')
        self.assertTrue(Ingrediente.objects.filter(pk=self.viejo.pk).exists())

    def test_ingrediente_compartido_no_se_duplica(self):
        otra = Hamburguesa.objects.create(nombre='Full', precio=15500, descripcion='Otra')
        Receta.objects.create(hamburguesa=otra, ingrediente=self.pan, cantidad_requerida=1)
        self.assertEqual(ingredientes_del_menu_activo().count(), 1)

    def test_adicional_activo_cuenta_solo_si_se_ofrece_en_una_activa(self):
        extra = Adicional.objects.create(nombre='Salsa extra', precio=1000)
        extra.hamburguesas.add(self.vieja)
        Receta.objects.create(adicional=extra, ingrediente=self.viejo, cantidad_requerida=1)
        self.assertNotIn(self.viejo, ingredientes_del_menu_activo())
        extra.hamburguesas.add(self.burger)
        self.assertIn(self.viejo, ingredientes_del_menu_activo())
        extra.activo = False
        extra.save()
        self.assertNotIn(self.viejo, ingredientes_del_menu_activo())

    def test_ingrediente_inactivo_no_aparece(self):
        self.pan.activo = False
        self.pan.save()
        self.assertFalse(ingredientes_del_menu_activo().exists())

    def test_inicio_y_movimientos_usan_el_mismo_filtro(self):
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.context['faltantes_count'], 1)
        self.assertEqual(list(MovimientoForm().fields['ingrediente'].queryset), [self.pan])
        response = self.client.get(reverse('inventario:registrar_movimiento'))
        self.assertNotContains(response, 'Salsa vieja')
        self.assertNotContains(response, 'Sin uso')

    def test_desactivar_hamburguesa_actualiza_inventario_y_vacio(self):
        self.burger.activa = False
        self.burger.save()
        response = self.client.get(reverse('inventario:ver_inventario'))
        self.assertEqual(list(response.context['ingredientes']), [])
        self.assertEqual(response.context['sin_contar'], [])
        self.assertContains(response, 'El menú activo todavía no tiene ingredientes asociados')
