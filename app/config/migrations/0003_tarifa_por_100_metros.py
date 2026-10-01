from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


def convertir_tarifa(apps, schema_editor):
    Configuracion = apps.get_model('config', 'Configuracion')
    for configuracion in Configuracion.objects.using(schema_editor.connection.alias).all():
        configuracion.tarifa_100m /= Decimal('10')
        configuracion.save(update_fields=['tarifa_100m'])


def restaurar_tarifa(apps, schema_editor):
    Configuracion = apps.get_model('config', 'Configuracion')
    for configuracion in Configuracion.objects.using(schema_editor.connection.alias).all():
        configuracion.tarifa_100m *= Decimal('10')
        configuracion.save(update_fields=['tarifa_100m'])


class Migration(migrations.Migration):
    dependencies = [('config', '0002_configuracion_whatsapp_cocina')]

    operations = [
        migrations.RenameField('configuracion', 'tarifa_km', 'tarifa_100m'),
        migrations.AlterField(
            model_name='configuracion', name='tarifa_100m',
            field=models.DecimalField(
                decimal_places=2, default=50, max_digits=10,
                validators=[MinValueValidator(0)],
                verbose_name='Tarifa por cada 100 metros ($)',
            ),
        ),
        migrations.RunPython(convertir_tarifa, restaurar_tarifa),
    ]
