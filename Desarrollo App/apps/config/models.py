"""
Modelo del app "config": los parámetros que el dueño del local puede cambiar
sin tocar código (tarifas de envío, costo de mano de obra).

Está implementado como SINGLETON: hay una sola fila en la tabla, siempre.
No tiene sentido tener "varias configuraciones del sistema".
"""

from django.db import models


class SystemConfig(models.Model):
    """La única fila de configuración. Se accede siempre con SystemConfig.get_config()."""

    tarifa_km = models.PositiveIntegerField(default=500)              # pesos por kilómetro
    distancia_minima = models.DecimalField(max_digits=5, decimal_places=2, default=1)  # km sin cargo
    costo_minimo_envio = models.PositiveIntegerField(default=1000)    # piso del envío
    costo_hora_mano_obra = models.PositiveIntegerField(default=2500)  # se usa en el cálculo de costos

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"

    def save(self, *args, **kwargs):
        """
        Fuerza que SIEMPRE se guarde en la fila 1.

        Si alguien intenta crear una segunda configuración, esto la pisa sobre
        la existente en vez de agregar una fila nueva. Es lo que garantiza
        que haya una sola.
        """
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Se anula el borrado a propósito: sin configuración el sistema no funciona."""
        pass

    @classmethod
    def get_config(cls):
        """
        Devuelve la configuración, creándola con los valores por defecto si es
        la primera vez que se pide.

        get_or_create devuelve una tupla (objeto, se_creó?); acá solo interesa
        el objeto, por eso el segundo valor se descarta.

        Es @classmethod (no recibe self sino la clase), así se puede llamar
        sin tener una instancia: SystemConfig.get_config()
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuración del Sistema"
