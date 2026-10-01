from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase

from .forms import ConfiguracionForm
from .models import Configuracion


class ConfiguracionTests(TestCase):
    def test_distancia_minima_no_admite_dos_decimales(self):
        form = ConfiguracionForm(data={
            'tarifa_100m': '50', 'distancia_minima': '1.25', 'costo_minimo_envio': '1000',
            'costo_hora_mano_obra': '2500', 'whatsapp_cocina': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('distancia_minima', form.errors)

    def test_distancia_minima_se_muestra_sin_segundo_decimal_historico(self):
        config = Configuracion(distancia_minima=Decimal('1.10'))
        form = ConfiguracionForm(instance=config)
        self.assertEqual(form.initial['distancia_minima'], '1.1')

    def test_tarifa_negativa_invalida(self):
        form = ConfiguracionForm(data={
            'tarifa_100m': '-1', 'distancia_minima': '0.1', 'costo_minimo_envio': '0',
            'costo_hora_mano_obra': '2500', 'whatsapp_cocina': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('tarifa_100m', form.errors)

    def test_tarifa_decimal_valida(self):
        form = ConfiguracionForm(data={
            'tarifa_100m': '55.50', 'distancia_minima': '0.1', 'costo_minimo_envio': '0',
            'costo_hora_mano_obra': '2500', 'whatsapp_cocina': '+54 9 12345678',
        })
        self.assertTrue(form.is_valid(), form.errors)
        config = form.save()
        self.assertEqual(config.tarifa_100m, Decimal('55.50'))
        self.assertEqual(config.whatsapp_cocina, '54912345678')


class MigracionTarifaTests(TransactionTestCase):
    def test_convierte_tarifa_anterior_sin_cambiar_precio(self):
        executor = MigrationExecutor(connection)
        try:
            executor.migrate([('config', '0002_configuracion_whatsapp_cocina')])
            anterior = executor.loader.project_state([('config', '0002_configuracion_whatsapp_cocina')]).apps
            anterior.get_model('config', 'Configuracion').objects.update_or_create(pk=1, defaults={'tarifa_km': 555})
            executor = MigrationExecutor(connection)
            executor.migrate([('config', '0003_tarifa_por_100_metros')])
            self.assertEqual(Configuracion.objects.get(pk=1).tarifa_100m, Decimal('55.50'))
        finally:
            MigrationExecutor(connection).migrate([('config', '0003_tarifa_por_100_metros')])
