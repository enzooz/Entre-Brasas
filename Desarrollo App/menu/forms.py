"""
Formularios de la app Menu.

Un ModelForm de Django hace tres cosas por nosotros:
  1. arma los campos HTML a partir del modelo,
  2. revisa que lo que escribio el usuario este bien,
  3. guarda en la base con form.save().
"""
from django import forms

from .models import Hamburguesa, Adicional


class HamburguesaForm(forms.ModelForm):
    class Meta:
        model = Hamburguesa

        # Solo listamos los campos que carga el usuario.
        # "activa" no esta porque se maneja con el boton de activar/desactivar.
        fields = ['nombre', 'descripcion', 'precio', 'incluye_papas']

        # widgets sirve para decidir como se ve cada campo en la pantalla.
        # Lo usamos sobre todo para ponerle la clase de CSS y que tome los estilos.
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'incluye_papas': forms.CheckboxInput(),
        }

        # Reemplaza el mensaje de error que trae Django por uno en castellano.
        error_messages = {
            'nombre': {'unique': 'Ya existe una hamburguesa con ese nombre'},
        }

    def clean_precio(self):
        """
        Revisa que el precio sea valido.

        Django busca solo los metodos que empiezan con clean_ seguido del
        nombre de un campo, y los ejecuta cuando se llama a form.is_valid().

        Si algo esta mal, se lanza un ValidationError y el error aparece
        al lado del campo. Si esta bien, hay que DEVOLVER el valor.
        """
        precio = self.cleaned_data.get('precio')

        if precio <= 0:
            raise forms.ValidationError('El precio tiene que ser mayor a 0')

        return precio


class AdicionalForm(forms.ModelForm):
    # Este campo lo escribimos a mano en vez de dejar que Django lo arme solo,
    # porque necesitamos que sea obligatorio. Las relaciones de muchos a muchos
    # vienen como opcionales por defecto, y queremos que el adicional este
    # asociado por lo menos a una hamburguesa.
    #
    #   queryset -> que opciones se muestran
    #   widget   -> como se muestran (una casilla por hamburguesa)
    #   required -> que sea obligatorio elegir alguna
    hamburguesas = forms.ModelMultipleChoiceField(
        queryset=Hamburguesa.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'required': 'Hay que elegir al menos una hamburguesa'}
    )

    class Meta:
        model = Adicional
        fields = ['nombre', 'precio', 'hamburguesas']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

        error_messages = {
            'nombre': {'unique': 'Ya existe un adicional con ese nombre'},
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')

        if precio <= 0:
            raise forms.ValidationError('El precio tiene que ser mayor a 0')

        return precio
