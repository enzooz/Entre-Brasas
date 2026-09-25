"""
Modelos de la app Inventario.

Son tres tablas que trabajan juntas:

    Ingrediente          -> que insumos hay y cuanto queda de cada uno
    Receta               -> cuanto de cada insumo lleva cada producto
    MovimientoInventario -> el registro de todas las entradas y salidas

La idea: cuando un pedido pasa a "en preparacion", el sistema mira la receta
de cada hamburguesa, descuenta del stock y deja anotado el movimiento.
"""
from django.db import models
from menu.models import Hamburguesa, Adicional


class Ingrediente(models.Model):
    """Un insumo de la cocina: carne, pan, queso, aceite, etc."""

    UNIDADES = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('L', 'Litros'),
        ('mL', 'Mililitros'),
        ('unidades', 'Unidades'),
    ]

    nombre = models.CharField(max_length=100, unique=True)

    # DecimalField y no numero entero porque el stock puede tener decimales
    # (2.50 kg de carne). max_digits=10 y decimal_places=2 quiere decir
    # que admite hasta 99.999.999,99
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    unidad = models.CharField(max_length=10, choices=UNIDADES)

    # Cuando el stock baja de este valor, el sistema avisa que hay que reponer.
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2)

    # Precio de la ultima compra, en pesos por unidad.
    # Se usa para calcular cuanto cuesta hacer cada hamburguesa.
    precio_compra = models.PositiveIntegerField(default=0)

    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"

    @property
    def stock_bajo(self):
        """
        Devuelve True si hay que reponer este ingrediente.

        Es una property: se usa como si fuera un dato guardado
        (ingrediente.stock_bajo) pero en realidad se calcula en el momento
        y no ocupa lugar en la base de datos.
        """
        return self.stock_actual < self.stock_minimo

    def __str__(self):
        return self.nombre


class Receta(models.Model):
    """
    Una linea de receta: "la hamburguesa X lleva 0.20 kg de carne".

    La receta completa de un producto son varias filas de estas.

    Una receta pertenece A UNA hamburguesa O A UN adicional, nunca a los dos.
    El campo que no corresponde queda vacio (en NULL). Por eso los dos
    campos tienen null=True y blank=True.
    """

    # null=True  -> en la base de datos puede quedar vacio
    # blank=True -> en los formularios no es obligatorio
    # on_delete=CASCADE -> si se borra la hamburguesa, se borran sus recetas
    hamburguesa = models.ForeignKey(
        Hamburguesa,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='recetas'
    )

    adicional = models.ForeignKey(
        Adicional,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='recetas'
    )

    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.CASCADE,
        related_name='recetas'
    )

    # Cuanto de ese ingrediente lleva UNA unidad del producto.
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['ingrediente']
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"

    @property
    def producto(self):
        """Devuelve el producto de esta receta, sea hamburguesa o adicional."""
        if self.hamburguesa:
            return self.hamburguesa
        return self.adicional

    def __str__(self):
        return f"{self.producto} - {self.ingrediente.nombre}"


class MovimientoInventario(models.Model):
    """
    El registro de todas las entradas y salidas de stock.

    No se borra ni se edita nunca: si hay que revertir algo, se crea el
    movimiento contrario. Asi queda el historial completo de que paso.
    """

    TIPOS = [
        ('entrada', 'Entrada'),   # una compra, una devolucion
        ('salida', 'Salida'),     # consumo de un pedido, una perdida
    ]

    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )

    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    # Siempre hay que decir por que se movio el stock, para poder revisarlo despues.
    motivo = models.CharField(max_length=255)

    # Precio pagado por unidad (solo se completa en las compras).
    precio_unitario = models.PositiveIntegerField(default=0)

    # auto_now_add: Django pone la fecha y hora solos al crear el registro.
    fecha = models.DateTimeField(auto_now_add=True)

    # Si el movimiento lo genero un pedido, queda anotado cual.
    # Si fue una compra hecha a mano, este campo queda vacio.
    # on_delete=SET_NULL -> si se borra el pedido, el movimiento no se borra:
    # solo se le vacia este campo, asi no se pierde el historial de stock.
    pedido_relacionado = models.ForeignKey(
        'pedidos.Pedido',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='movimientos'
    )

    class Meta:
        ordering = ['-fecha']  # el guion hace que sea de mas nuevo a mas viejo
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.ingrediente.nombre} ({self.cantidad})"
