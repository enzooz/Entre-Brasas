"""
Modelo de la app Config.

Guarda los valores que el duenio del local puede cambiar desde la pantalla
de configuracion, sin tocar el codigo: tarifas de envio y costo de la hora
de trabajo.

Hay una sola fila de configuracion en toda la base (la fila numero 1).
No tendria sentido tener varias "configuraciones del sistema".
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Configuracion(models.Model):
    """Los parametros generales del sistema."""

    # Precio de 0,1 km (100 metros). Admite centavos para convertir tarifas
    # anteriores sin cambiar el importe que se venia cobrando.
    tarifa_100m = models.DecimalField(
        max_digits=10, decimal_places=2, default=50,
        validators=[MinValueValidator(0)], verbose_name='Tarifa por cada 100 metros ($)',
    )

    # Distancia cubierta por el envio minimo; solo el excedente suma tarifa.
    distancia_minima = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    # Precio del tramo incluido, incluso para envios mas cortos.
    costo_minimo_envio = models.PositiveIntegerField(default=1000)

    # Se usa para calcular cuanto cuesta preparar cada hamburguesa.
    costo_hora_mano_obra = models.PositiveIntegerField(default=2500)

    # El numero de WhatsApp del celular de la cocina, con codigo de pais y
    # sin espacios (por ejemplo 5493624000000). Si esta cargado, el detalle
    # del pedido muestra un boton que abre WhatsApp con la comanda ya escrita.
    whatsapp_cocina = models.CharField(max_length=30, blank=True)

    geoapify_api_key = models.CharField(max_length=128, blank=True)
    local_latitud = models.FloatField(default=-27.455266, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    local_longitud = models.FloatField(default=-58.992536, validators=[MinValueValidator(-180), MaxValueValidator(180)])

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
