from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Compra, Producto

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['direccion', 'rol']


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'costo', 'activo']


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['producto', 'cantidad']
