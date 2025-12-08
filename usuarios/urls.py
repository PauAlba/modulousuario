from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('editar/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    path('productos/', views.ProductosView.as_view(), name='productos'),
    path('productos/crear/', views.CrearProductoView.as_view(), name='crear_producto'),
    path('comprar/', views.comprar_view, name='comprar'),
]