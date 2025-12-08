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

class EditarPerfilForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = PerfilUsuario
        fields = ['direccion', 'email']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Prellenar correo
        if user:
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        perfil = super().save(commit=False)

        # Guardar correo en User
        perfil.user.email = self.cleaned_data['email']

        if commit:
            perfil.user.save()
            perfil.save()

        return perfil

