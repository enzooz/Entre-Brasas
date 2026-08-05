from django.db import models


class SystemConfig(models.Model):
    tarifa_km = models.PositiveIntegerField(default=500)
    distancia_minima = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    costo_minimo_envio = models.PositiveIntegerField(default=1000)
    costo_hora_mano_obra = models.PositiveIntegerField(default=2500)

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_config(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuración del Sistema"
