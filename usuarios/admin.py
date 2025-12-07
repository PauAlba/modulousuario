from django.contrib import admin
from .models import PerfilUsuario, Producto, Compra

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'direccion', 'rol')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'costo', 'activo', 'creado_en')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'categoria')

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'precio_unitario', 'total', 'fecha')
    list_filter = ('fecha', 'producto')
    search_fields = ('usuario__username', 'producto__nombre')
