from django.db import migrations, models
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):
    dependencies = [('config', '0003_tarifa_por_100_metros')]
    operations = [
        migrations.AddField('configuracion', 'geoapify_api_key', models.CharField(blank=True, max_length=128)),
        migrations.AddField('configuracion', 'local_latitud', models.FloatField(default=-27.455266, validators=[MinValueValidator(-90), MaxValueValidator(90)])),
        migrations.AddField('configuracion', 'local_longitud', models.FloatField(default=-58.992536, validators=[MinValueValidator(-180), MaxValueValidator(180)])),
    ]
