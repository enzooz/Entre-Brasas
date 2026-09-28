"""
Modelo de la app Config.

Guarda los valores que el duenio del local puede cambiar desde la pantalla
de configuracion, sin tocar el codigo: tarifas de envio y costo de la hora
de trabajo.

Hay una sola fila de configuracion en toda la base (la fila numero 1).
No tendria sentido tener varias "configuraciones del sistema".
"""
from django.db import models


class Configuracion(models.Model):
    """Los parametros generales del sistema."""

    # Cuanto se cobra por cada kilometro de distancia.
    tarifa_km = models.PositiveIntegerField(default=500)

    # Hasta esta distancia no se cobra envio (es "a la vuelta").
    distancia_minima = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    # El envio nunca puede salir menos que esto.
    costo_minimo_envio = models.PositiveIntegerField(default=1000)

    # Se usa para calcular cuanto cuesta preparar cada hamburguesa.
    costo_hora_mano_obra = models.PositiveIntegerField(default=2500)

    # El numero de WhatsApp del celular de la cocina, con codigo de pais y
    # sin espacios (por ejemplo 5493624000000). Si esta cargado, el detalle
    # del pedido muestra un boton que abre WhatsApp con la comanda ya escrita.
    whatsapp_cocina = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "Configuracion"
        verbose_name_plural = "Configuraciones"

    @classmethod
    def get_config(cls):
        """
        Devuelve la configuracion del sistema.

        get_or_create busca la fila numero 1. Si existe la devuelve, y si no
        existe la crea con los valores por defecto de arriba. Asi la primera
        vez que se usa el sistema no hace falta cargar nada a mano.

        Devuelve dos cosas (el objeto y si lo tuvo que crear), pero a nosotros
        solo nos interesa el objeto.

        Es un classmethod: se llama sobre la clase, sin tener un objeto antes.
            Configuracion.get_config()
        """
        configuracion, creada = cls.objects.get_or_create(pk=1)
        return configuracion

    def __str__(self):
        return "Configuracion del Sistema"
