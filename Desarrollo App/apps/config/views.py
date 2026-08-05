from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SystemConfig
from .forms import SystemConfigForm


def admin_panel(request):
    config = SystemConfig.get_config()
    if request.method == 'POST':
        form = SystemConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada exitosamente')
            return redirect('config:admin_panel')
    else:
        form = SystemConfigForm(instance=config)
    return render(request, 'config/admin_panel.html', {'form': form})
