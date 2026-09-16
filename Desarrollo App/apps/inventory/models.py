"""
Modelos del app "inventory" (inventario).

Son tres tablas que trabajan juntas:

    Ingredient          -> qué insumos hay y cuánto stock queda de cada uno
    Recipe              -> cuánto de cada insumo lleva cada producto del menú
    InventoryMovement   -> la traza de TODAS las entradas y salidas de stock

La lógica: cuando un pedido pasa a "en preparación", el sistema mira la Recipe
de cada hamburguesa, descuenta de Ingredient.stock_actual y deja registrado
un InventoryMovement. (Eso pasa en apps/orders/services.py.)
"""

from django.db import models


class Ingredient(models.Model):
    """Un insumo de la cocina: carne, pan, queso, aceite, etc."""

    UNIDADES = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('L', 'Litros'),
        ('mL', 'Mililitros'),
        ('unidades', 'Unidades'),
    ]

    nombre = models.CharField(max_length=100, unique=True)  # unique: no se repiten nombres

    # DecimalField y no Float: con decimales exactos, sin errores de redondeo binario.
    # max_digits=10 y decimal_places=2 significa hasta 99.999.999,99
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad = models.CharField(max_length=10, choices=UNIDADES)

    # Umbral para el aviso de "stock bajo".
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2)

    precio_compra = models.PositiveIntegerField(default=0)  # Precio última compra en pesos
    activo = models.BooleanField(default=True)  # baja lógica: no se borra, se desactiva

    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        ordering = ['nombre']  # siempre alfabético

    @property
    def stock_bajo(self):
        """
        True si hay que reponer. Se usa en los templates como {{ i.stock_bajo }}.

        Ojo: esto se evalúa en Python, ingrediente por ingrediente. Para filtrar
        una lista entera conviene hacerlo en la base con F() (ver inventory/views.py).
        """
        return self.stock_actual < self.stock_minimo

    def __str__(self):
        return self.nombre


class Recipe(models.Model):
    """
    Una línea de receta: "la hamburguesa X lleva 0.20 kg del ingrediente Y".

    Una receta completa son varias filas de estas con el mismo producto.
    """

    TIPOS_PRODUCTO = [
        ('hamburger', 'Hamburguesa'),
        ('addon', 'Adicional'),
    ]

    # Acá hay una decisión importante: en vez de dos ForeignKey (una a Hamburger
    # y otra a Addon), se guarda el TIPO y el ID sueltos. Así una sola tabla sirve
    # para los dos productos.
    # La contra: la base no puede garantizar que ese producto_id exista de verdad
    # (no hay FOREIGN KEY), y si se borra una hamburguesa su receta queda huérfana.
    # Django tiene una herramienta para esto bien hecha (GenericForeignKey de contenttypes).
    producto_tipo = models.CharField(max_length=10, choices=TIPOS_PRODUCTO)
    producto_id = models.PositiveIntegerField()

    ingrediente = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recetas')
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        # Impide cargar dos veces el mismo ingrediente en la misma receta.
        # Es una restricción a nivel base de datos, no solo del formulario.
        unique_together = ['producto_tipo', 'producto_id', 'ingrediente']
        ordering = ['producto_tipo', 'producto_id']

    def __str__(self):
        return f"{self.get_producto_tipo_display()} #{self.producto_id} - {self.ingrediente.nombre}"


class InventoryMovement(models.Model):
    """
    El libro contable del stock: cada entrada y cada salida queda registrada.

    No se borra ni se edita nunca: si algo hay que revertir, se crea el movimiento
    inverso (ver devolver_stock en orders/services.py). Así el historial es auditable.
    """

    TIPOS = [
        ('entrada', 'Entrada'),   # compra, devolución, ajuste positivo
        ('salida', 'Salida'),     # consumo por pedido, merma, ajuste negativo
    ]

    ingrediente = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=255)  # obligatorio, para trazabilidad
    precio_unitario = models.PositiveIntegerField(default=0)  # Peso por unidad comprada
    fecha = models.DateTimeField(auto_now_add=True)

    # Si el movimiento vino de un pedido, queda el vínculo. Si fue una compra
    # manual, queda en NULL (por eso null=True).
    # SET_NULL: si se borra el pedido, el movimiento sobrevive con el campo vacío;
    # el historial de stock no se pierde.
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
        ordering = ['-fecha']  # el más reciente primero

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.ingrediente.nombre} ({self.cantidad})"
