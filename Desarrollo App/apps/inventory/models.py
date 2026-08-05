from django.db import models


class Ingredient(models.Model):
    UNIDADES = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('L', 'Litros'),
        ('mL', 'Mililitros'),
        ('unidades', 'Unidades'),
    ]
    nombre = models.CharField(max_length=100, unique=True)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad = models.CharField(max_length=10, choices=UNIDADES)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra = models.PositiveIntegerField(default=0)  # Precio última compra en pesos
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        ordering = ['nombre']

    @property
    def stock_bajo(self):
        return self.stock_actual < self.stock_minimo

    def __str__(self):
        return self.nombre


class Recipe(models.Model):
    TIPOS_PRODUCTO = [
        ('hamburger', 'Hamburguesa'),
        ('addon', 'Adicional'),
    ]
    producto_tipo = models.CharField(max_length=10, choices=TIPOS_PRODUCTO)
    producto_id = models.PositiveIntegerField()
    ingrediente = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recetas')
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        unique_together = ['producto_tipo', 'producto_id', 'ingrediente']
        ordering = ['producto_tipo', 'producto_id']

    def __str__(self):
        return f"{self.get_producto_tipo_display()} #{self.producto_id} - {self.ingrediente.nombre}"


class InventoryMovement(models.Model):
    TIPOS = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    ingrediente = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=255)
    precio_unitario = models.PositiveIntegerField(default=0)  # Peso por unidad comprada
    fecha = models.DateTimeField(auto_now_add=True)
    pedido_relacionado = models.ForeignKey(
        'orders.Order',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='movimientos_inventario'
    )

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.ingrediente.nombre} ({self.cantidad})"
