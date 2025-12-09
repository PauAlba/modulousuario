from django.contrib import admin
from .models import PerfilUsuario, Producto, Compra

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'direccion', 'rol')
    # filtro lateral para ver "solo Clientes" o "solo Admins"
    list_filter = ('rol',) 
    # buscador que busca dentro de la tabla User relacionada
    search_fields = ('user__username', 'user__email', 'direccion')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'costo', 'activo', 'creado_en')
    # filtro de 'creado_en' para filtrar productos nuevos vs viejos
    list_filter = ('categoria', 'activo', 'creado_en') 
    search_fields = ('nombre', 'categoria')
    # barra de navegación por fecha 
    date_hierarchy = 'creado_en' 

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'precio_unitario', 'total', 'fecha')
    list_filter = ('fecha', 'producto')
    search_fields = ('usuario__username', 'producto__nombre')
    # barra de navegación por fecha 
    date_hierarchy = 'fecha'