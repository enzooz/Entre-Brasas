"""
Vista del app "config": el panel donde se editan los parámetros del sistema.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SystemConfig
from .forms import SystemConfigForm


def admin_panel(request):
    """
    Pantalla única de configuración.

    Es siempre una EDICIÓN, nunca un alta: por eso se trae la config primero
    y se pasa como instance= tanto en el GET como en el POST.

    OJO: esta pantalla cambia las tarifas que se le cobran al cliente y
    no pide ningún tipo de login. Cualquiera que conozca la URL puede tocarlas.
    """
    config = SystemConfig.get_config()  # crea la fila si todavía no existía

    if request.method == 'POST':
        form = SystemConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada exitosamente')
            return redirect('config:admin_panel')
    else:
        form = SystemConfigForm(instance=config)  # precargado con los valores actuales

    return render(request, 'config/admin_panel.html', {'form': form})
