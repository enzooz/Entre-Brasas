from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('pedidos', '0003_itempedido_nota')]
    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('telefono', models.CharField(blank=True, max_length=50)),
                ('telefono_clave', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('direccion', models.CharField(blank=True, max_length=300)),
                ('fecha_alta', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['nombre', 'pk']},
        ),
        migrations.AddField(
            model_name='pedido', name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pedidos', to='pedidos.cliente'),
        ),
    ]
