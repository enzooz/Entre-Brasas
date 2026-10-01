import re

from django.db import migrations


def importar_clientes(apps, schema_editor):
    Cliente = apps.get_model('pedidos', 'Cliente')
    Pedido = apps.get_model('pedidos', 'Pedido')
    alias = schema_editor.connection.alias
    for pedido in Pedido.objects.using(alias).order_by('fecha_creacion', 'pk').iterator():
        telefono = pedido.cliente_telefono.strip()
        clave = re.sub(r'[^0-9]', '', telefono)
        if not re.fullmatch(r'[0-9+\s().-]+', telefono) or not 7 <= len(clave) <= 20:
            continue  # Sin identidad fiable: conservar el pedido sin fusionar nombres.
        cliente, creado = Cliente.objects.using(alias).get_or_create(
            telefono_clave=clave,
            defaults={'nombre': pedido.cliente_nombre.strip(), 'telefono': telefono, 'direccion': pedido.cliente_direccion.strip()},
        )
        cambios = {'telefono': telefono, 'fecha_actualizacion': pedido.fecha_creacion}
        if creado:
            cambios['fecha_alta'] = pedido.fecha_creacion
        if pedido.cliente_nombre.strip():
            cambios['nombre'] = pedido.cliente_nombre.strip()
        if pedido.cliente_direccion.strip():
            cambios['direccion'] = pedido.cliente_direccion.strip()
        Cliente.objects.using(alias).filter(pk=cliente.pk).update(**cambios)
        Pedido.objects.using(alias).filter(pk=pedido.pk).update(cliente_id=cliente.pk)


class Migration(migrations.Migration):
    dependencies = [('pedidos', '0004_cliente')]
    operations = [migrations.RunPython(importar_clientes, migrations.RunPython.noop)]
