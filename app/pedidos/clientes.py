"""Identidad por teléfono, sin adivinar país ni unir personas por su nombre."""
import re

from .models import Cliente


def normalizar_telefono(telefono):
    if not re.fullmatch(r'[0-9+\s().-]+', telefono or ''):
        return None
    digitos = re.sub(r'[^0-9]', '', telefono or '')
    return digitos if 7 <= len(digitos) <= 20 else None


def cliente_para_pedido(datos):
    """Se llama dentro de la transacción del pedido, nunca al autocompletar."""
    nombre = datos.get('cliente_nombre', '').strip()
    telefono = datos.get('cliente_telefono', '').strip()
    direccion = datos.get('cliente_direccion', '').strip()
    clave = normalizar_telefono(telefono)
    if clave:
        cliente, _ = Cliente.objects.get_or_create(
            telefono_clave=clave, defaults={'nombre': nombre, 'telefono': telefono, 'direccion': direccion},
        )
    else:
        # Sin teléfono, reutilizar únicamente una elección explícita que siga
        # correspondiendo al mismo nombre. Los homónimos no se fusionan.
        elegido = datos.get('cliente_id', '')
        cliente = Cliente.objects.filter(pk=elegido, telefono_clave__isnull=True).first() if elegido else None
        if cliente is None or cliente.nombre.casefold() != nombre.casefold():
            cliente = Cliente.objects.create(nombre=nombre, direccion=direccion)
    cliente.nombre = nombre
    if telefono:
        cliente.telefono = telefono
    if direccion:
        cliente.direccion = direccion
    cliente.save()
    return cliente
