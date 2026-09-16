"""
Modelos del app "menu": lo que el local vende.

    Hamburger -> los productos principales
    Addon     -> los extras que se le pueden agregar (bacon, doble carne, etc.)

Los precios se guardan acá como referencia actual. Cuando se arma un pedido,
el precio se COPIA al OrderItem (ver orders/models.py), así cambiar un precio
hoy no altera los pedidos de ayer.
"""

from django.db import models


class Hamburger(models.Model):
    """Un producto del menú."""

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    precio_base = models.PositiveIntegerField()  # En pesos argentinos
    incluye_papas = models.BooleanField(default=True)
    activa = models.BooleanField(default=True)  # baja lógica: se saca del menú sin borrarla

    class Meta:
        verbose_name = "Hamburguesa"
        verbose_name_plural = "Hamburguesas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Addon(models.Model):
    """
    Un adicional. La diferencia con Hamburger es la relación 'productos'.
    """

    nombre = models.CharField(max_length=100, unique=True)
    precio = models.PositiveIntegerField()  # En pesos argentinos

    # ManyToMany: un adicional puede aplicar a varias hamburguesas, y una
    # hamburguesa puede tener varios adicionales. Django crea sola una tabla
    # intermedia para vincularlos.
    # related_name='adicionales' permite preguntar al revés: hamburguesa.adicionales.all()
    productos = models.ManyToManyField(Hamburger, related_name='adicionales', blank=True)

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Adicional"
        verbose_name_plural = "Adicionales"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
