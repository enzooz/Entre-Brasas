"""
Formularios del app "orders".

Un ModelForm de Django hace tres cosas a la vez:
  1. genera los campos HTML a partir del modelo,
  2. valida lo que el usuario escribió,
  3. guarda directo en la base con form.save().

ATENCIÓN: este archivo hoy es código muerto. OrderForm está escrito y funciona,
pero create_order() en views.py no lo usa: lee el POST a mano. O sea que la
validación del teléfono de más abajo NUNCA se ejecuta.
Conectarlo es el arreglo más rentable del proyecto.
"""

from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        # model le dice de qué modelo sacar los campos.
        model = Order
        # fields lista qué campos exponer. Los que NO están acá (estado, total,
        # costo_envio, fecha_creacion) los calcula el sistema, no el usuario.
        fields = [
            'cliente_nombre', 'cliente_telefono', 'cliente_direccion',
            'observaciones', 'metodo_pago', 'distancia_km', 'retiro_local'
        ]
        # widgets controla el HTML que se genera. Acá se usa sobre todo para
        # ponerle la clase CSS 'form-control' a cada input y que herede los estilos.
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            # min y step se traducen a atributos HTML: el navegador ya valida un poco.
            'distancia_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'retiro_local': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_cliente_telefono(self):
        """
        Validación de un campo puntual.

        Django busca automáticamente los métodos que se llamen clean_NOMBREDELCAMPO
        y los ejecuta al llamar form.is_valid(). Si el método lanza ValidationError,
        el formulario queda inválido y el error se muestra al lado del input.
        Si todo está bien, tiene que DEVOLVER el valor (si no, se guarda None).
        """
        telefono = self.cleaned_data.get('cliente_telefono')
        # El import debería estar arriba del archivo, no adentro del método.
        import re
        # Acepta dígitos, espacios, guiones, paréntesis y el signo +.
        # Sirve para formatos como +54 11 5555-1234 o (011) 4444-3333.
        if not re.match(r'^[\d\s\-\(\)+]+$', telefono):
            raise forms.ValidationError('Ingrese un número de teléfono válido')
        return telefono
