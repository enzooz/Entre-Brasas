"""
Modelos de la app Menu.

Aca se define QUE VENDE el local: las hamburguesas y los adicionales.

Un modelo es una clase de Python que representa una tabla de la base de datos.
Cada atributo de la clase es una columna de esa tabla.
"""
from django.db import models


class Hamburguesa(models.Model):
    """Una hamburguesa del menu."""

    # unique=True significa que no puede haber dos hamburguesas con el mismo nombre.
    nombre = models.CharField(max_length=100, unique=True)

    descripcion = models.TextField()

    # El precio se guarda como numero entero de pesos (sin centavos).
    # PositiveIntegerField = entero que no admite valores negativos.
    precio = models.PositiveIntegerField()

    incluye_papas = models.BooleanField(default=True)

    # En vez de borrar una hamburguesa la desactivamos, asi los pedidos
    # viejos que la incluyen siguen teniendo sentido.
    activa = models.BooleanField(default=True)

    class Meta:
        # Cuando pidamos las hamburguesas, van a venir ordenadas por nombre.
        ordering = ['nombre']
        # Nombres en castellano para los mensajes que arma Django solo.
        verbose_name = "Hamburguesa"
        verbose_name_plural = "Hamburguesas"

    def __str__(self):
        """Texto que se muestra cuando se imprime el objeto."""
        return self.nombre


class Adicional(models.Model):
    """Un extra que se le puede agregar a una hamburguesa (bacon, huevo, etc)."""

    nombre = models.CharField(max_length=100, unique=True)
    precio = models.PositiveIntegerField()

    # Relacion de muchos a muchos:
    #   un adicional puede estar disponible en varias hamburguesas,
    #   y una hamburguesa puede tener varios adicionales.
    # Django crea sola una tabla intermedia para guardar estos vinculos.
    #
    # related_name='adicionales' nos deja preguntar al reves:
    #   hamburguesa.adicionales.all()  ->  los adicionales de esa hamburguesa
    hamburguesas = models.ManyToManyField(
        Hamburguesa,
        related_name='adicionales',
        blank=True
    )

    activo = models.BooleanField(default=True)

    # Marca el adicional que convierte una hamburguesa en "doble" o "triple"
    # (el Medallon extra). Con esto el formulario de pedidos muestra el
    # selector Simple / Doble / Triple y la comanda escribe "Crispy doble".
    es_medallon_extra = models.BooleanField(
        default=False,
        verbose_name='Es el medallon extra (doble / triple)'
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = "Adicional"
        verbose_name_plural = "Adicionales"

    def __str__(self):
        return self.nombre
