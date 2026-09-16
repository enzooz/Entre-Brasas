"""
Modelos del app "orders" (pedidos).

Cada clase de acá es una tabla en la base de datos. Django traduce estos
modelos a SQL mediante las migraciones (ver migrations/0001_initial.py).

La estructura es jerárquica:
    Order (el pedido)
      └─ OrderItem (cada hamburguesa pedida)
           └─ OrderItemAddon (cada adicional de esa hamburguesa)
    Order también tiene OrderStatusHistory (la traza de cambios de estado)
"""

from django.db import models


class Order(models.Model):
    """Un pedido completo: los datos del cliente, el envío y el total."""

    # ESTADOS define el flujo de vida del pedido. Cada tupla es (valor_en_db, texto_visible).
    # El valor de la izquierda es lo que se guarda; el de la derecha es lo que ve el usuario.
    # Django genera solo el método get_estado_display() para obtener el texto visible.
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

    # --- Datos del cliente ---
    cliente_nombre = models.CharField(max_length=200)
    cliente_telefono = models.CharField(max_length=50)   # CharField y no número: admite guiones, paréntesis, +54
    cliente_direccion = models.CharField(max_length=300)
    observaciones = models.TextField(blank=True, null=True)  # blank=opcional en formularios, null=puede ser NULL en la DB

    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)

    # --- Envío ---
    # DecimalField para la distancia porque necesitamos decimales exactos (3.50 km).
    distancia_km = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # La plata se guarda como entero de pesos (sin centavos), porque en Argentina
    # los precios de este rubro son redondos. PositiveIntegerField = no admite negativos.
    costo_envio = models.PositiveIntegerField(default=0)
    retiro_local = models.BooleanField(default=False)  # si es True, el envío no se cobra

    total = models.PositiveIntegerField(default=0)  # se calcula en services.calcular_total()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # auto_now_add: se setea solo al crear, nunca cambia

    class Meta:
        # verbose_name controla cómo se nombra el modelo en textos generados por Django.
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        # ordering define el ORDER BY por defecto: los pedidos salen del más viejo al más nuevo
        # (lógico para una cola de cocina: se atiende por orden de llegada).
        ordering = ['fecha_creacion']

    def __str__(self):
        # Lo que se muestra cuando Python convierte el objeto a texto.
        return f"Pedido #{self.pk} - {self.cliente_nombre}"


class OrderItem(models.Model):
    """Una línea del pedido: tal hamburguesa, tantas unidades, a tal precio."""

    # ForeignKey = relación "muchos a uno". Muchos items pertenecen a un pedido.
    # related_name='items' permite hacer order.items.all() desde el pedido.
    # on_delete=CASCADE: si se borra el pedido, se borran sus items.
    pedido = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    # 'menu.Hamburger' como string evita un import circular entre apps.
    hamburguesa = models.ForeignKey('menu.Hamburger', on_delete=models.CASCADE)

    cantidad = models.PositiveIntegerField(default=1)

    # Clave: se guarda una COPIA del precio al momento del pedido.
    # Si mañana sube el precio de la hamburguesa, los pedidos viejos no se alteran.
    precio_unitario = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Item del Pedido"
        verbose_name_plural = "Items del Pedido"

    @property
    def subtotal(self):
        """
        Precio de la línea sin contar adicionales.
        Es @property: se usa como atributo (item.subtotal), no como método,
        y no se guarda en la DB — se calcula cada vez que se pide.
        """
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.hamburguesa.nombre} x{self.cantidad}"


class OrderItemAddon(models.Model):
    """Un adicional aplicado a un item concreto (ej: bacon extra en LA hamburguesa 2)."""

    item = models.ForeignKey(OrderItem, related_name='adicionales', on_delete=models.CASCADE)
    adicional = models.ForeignKey('menu.Addon', on_delete=models.CASCADE)
    # Igual que en OrderItem: se congela el precio histórico del adicional.
    precio = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Adicional del Item"
        verbose_name_plural = "Adicionales del Item"

    def __str__(self):
        return f"{self.adicional.nombre}"


class OrderStatusHistory(models.Model):
    """
    Traza de auditoría: registra cada cambio de estado del pedido.

    Sirve para responder "¿a qué hora salió este pedido?" o "¿por qué se canceló?".
    Se escribe desde las vistas advance_order() y cancel_order().
    """

    pedido = models.ForeignKey(Order, related_name='historial', on_delete=models.CASCADE)
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    observacion = models.TextField(blank=True, null=True)  # acá se guarda el motivo de cancelación
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de Estado"
        verbose_name_plural = "Historial de Estados"
        # El "-" invierte el orden: del cambio más reciente al más viejo.
        ordering = ['-fecha']

    def __str__(self):
        return f"Pedido #{self.pedido.pk}: {self.estado_anterior} → {self.estado_nuevo}"
