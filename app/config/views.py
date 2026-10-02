"""
Vista de la app Config: la pantalla donde se cambian las tarifas del sistema.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.debug import sensitive_post_parameters

from .models import Configuracion
from .forms import ConfiguracionForm


@sensitive_post_parameters('geoapify_api_key')
def panel_config(request):
    """
    Pantalla de configuracion.

    Siempre es una edicion, nunca un alta: por eso traemos la configuracion
    primero y se la pasamos al formulario con instance=, tanto cuando se
    muestra la pantalla como cuando se guarda.
    """
    configuracion = Configuracion.get_config()

    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, instance=configuracion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuracion guardada correctamente')
            return redirect('config:panel_config')
    else:
        form = ConfiguracionForm(instance=configuracion)

    return render(request, 'config/panel_config.html', {'form': form})
