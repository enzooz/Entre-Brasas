from django.db import models


class Order(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En preparación'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia/QR'),
    ]

    cliente_nombre = models.CharField(max_length=200)
    cliente_telefono = models.CharField(max_length=50)
    cliente_direccion = models.CharField(max_length=300)
    observaciones = models.TextField(blank=True, null=True)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    distancia_km = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    costo_envio = models.PositiveIntegerField(default=0)
    retiro_local = models.BooleanField(default=False)
    total = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['fecha_creacion']

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente_nombre}"


class OrderItem(models.Model):
    pedido = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    hamburguesa = models.ForeignKey('menu.Hamburger', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Item del Pedido"
        verbose_name_plural = "Items del Pedido"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.hamburguesa.nombre} x{self.cantidad}"


class OrderItemAddon(models.Model):
    item = models.ForeignKey(OrderItem, related_name='adicionales', on_delete=models.CASCADE)
    adicional = models.ForeignKey('menu.Addon', on_delete=models.CASCADE)
    precio = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Adicional del Item"
        verbose_name_plural = "Adicionales del Item"

    def __str__(self):
        return f"{self.adicional.nombre}"


class OrderStatusHistory(models.Model):
    pedido = models.ForeignKey(Order, related_name='historial', on_delete=models.CASCADE)
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    observacion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de Estado"
        verbose_name_plural = "Historial de Estados"
        ordering = ['-fecha']

    def __str__(self):
        return f"Pedido #{self.pedido.pk}: {self.estado_anterior} → {self.estado_nuevo}"
