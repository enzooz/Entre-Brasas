from django.db import models


class Hamburger(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    precio_base = models.PositiveIntegerField()  # En pesos argentinos
    incluye_papas = models.BooleanField(default=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hamburguesa"
        verbose_name_plural = "Hamburguesas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Addon(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    precio = models.PositiveIntegerField()  # En pesos argentinos
    productos = models.ManyToManyField(Hamburger, related_name='adicionales', blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Adicional"
        verbose_name_plural = "Adicionales"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
