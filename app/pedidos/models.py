"""
Modelos de la app Pedidos.

La estructura es una jerarquia de cuatro tablas:

    Pedido                      el pedido de un cliente
      |__ ItemPedido            cada hamburguesa pedida
            |__ AdicionalDeItem cada extra de esa hamburguesa
      |__ HistorialEstado       el registro de los cambios de estado
"""
from django.db import models


class Pedido(models.Model):
    """Un pedido completo: datos del cliente, envio, total y estado."""

    # Los estados por los que pasa un pedido.
    # Cada par es (lo_que_se_guarda, lo_que_se_muestra).
    # Django crea solo el metodo get_estado_display() para obtener el texto.
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En preparacion'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    # El recorrido de un pedido, escrito como diccionario: la clave es el
    # estado de ahora y el valor es el que sigue. Los estados finales
    # (entregado y cancelado) no estan porque despues de ellos no hay nada.
    SIGUIENTE_ESTADO = {
        'pendiente': 'en_preparacion',
        'en_preparacion': 'en_camino',
        'en_camino': 'entregado',
    }

    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia/QR'),
    ]

    # --- Datos del cliente ---
    cliente_nombre = models.CharField(max_length=200)
    # Es texto y no numero porque puede tener guiones, parentesis y el signo +.
    cliente_telefono = models.CharField(max_length=50)
    cliente_direccion = models.CharField(max_length=300)
    observaciones = models.TextField(blank=True, null=True)

    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)

    # --- Envio ---
    distancia_km = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    costo_envio = models.PositiveIntegerField(default=0)
    retiro_local = models.BooleanField(default=False)

    # El total se calcula al crear el pedido (ver pedidos/calculos.py).
    total = models.PositiveIntegerField(default=0)

    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Del mas viejo al mas nuevo: es una cola de cocina, se atiende por
        # orden de llegada.
        ordering = ['fecha_creacion']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    @property
    def siguiente_estado(self):
        """
        El estado al que pasaria el pedido si se avanza.

        Devuelve None si el pedido ya esta entregado o cancelado.
        """
        return self.SIGUIENTE_ESTADO.get(self.estado)

    @property
    def siguiente_estado_display(self):
        """El texto del siguiente estado ("En camino"), para mostrar en el boton."""
        return dict(self.ESTADOS).get(self.siguiente_estado, '')

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente_nombre}"


class ItemPedido(models.Model):
    """Una linea del pedido: tal hamburguesa, tantas unidades, a tal precio."""

    # ForeignKey es una relacion de muchos a uno:
    # muchos items pertenecen a un mismo pedido.
    # related_name='items' nos deja hacer: pedido.items.all()
    # on_delete=CASCADE: si se borra el pedido, se borran sus items.
    pedido = models.ForeignKey(
        Pedido,
        related_name='items',
        on_delete=models.CASCADE
    )

    hamburguesa = models.ForeignKey(
        'menu.Hamburguesa',
        on_delete=models.CASCADE,
        related_name='items_pedido'
    )

    cantidad = models.PositiveIntegerField(default=1)

    # Se guarda una COPIA del precio del momento de la venta.
    # Si manana sube el precio de la hamburguesa, los pedidos viejos
    # siguen mostrando lo que el cliente pago de verdad.
    precio_unitario = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Item del Pedido"
        verbose_name_plural = "Items del Pedido"

    @property
    def subtotal(self):
        """Lo que sale esta linea, sin contar los adicionales."""
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.hamburguesa.nombre} x{self.cantidad}"


class AdicionalDeItem(models.Model):
    """Un extra aplicado a un item concreto del pedido."""

    item = models.ForeignKey(
        ItemPedido,
        related_name='adicionales',
        on_delete=models.CASCADE
    )

    adicional = models.ForeignKey(
        'menu.Adicional',
        on_delete=models.CASCADE,
        related_name='items_pedido'
    )

    # Igual que en ItemPedido: se congela el precio del momento de la venta.
    precio = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Adicional del Item"
        verbose_name_plural = "Adicionales del Item"

    def __str__(self):
        return self.adicional.nombre


class HistorialEstado(models.Model):
    """
    Registro de cada cambio de estado de un pedido.

    Sirve para saber a que hora salio un pedido o por que se cancelo.
    """

    pedido = models.ForeignKey(
        Pedido,
        related_name='historial',
        on_delete=models.CASCADE
    )

    # Llevan los mismos choices que Pedido.estado para que Django arme
    # get_estado_anterior_display() y get_estado_nuevo_display(), que
    # devuelven el texto lindo ("En preparacion") en vez de "en_preparacion".
    estado_anterior = models.CharField(max_length=20, choices=Pedido.ESTADOS)
    estado_nuevo = models.CharField(max_length=20, choices=Pedido.ESTADOS)

    # Aca se guarda el motivo cuando se cancela un pedido.
    observacion = models.TextField(blank=True, null=True)

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Historial de Estado"
        verbose_name_plural = "Historial de Estados"

    def __str__(self):
        return f"Pedido #{self.pedido.pk}: {self.estado_anterior} a {self.estado_nuevo}"
