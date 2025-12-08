from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import PerfilUsuario, Producto, Compra
from .forms import EditarPerfilForm, RegistroForm, ProductoForm, CompraForm


# --- LOGIN ---

# def login_view(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#
#         user = authenticate(username=username, password=password)
#
#         if user:
#             login(request, user)
#             return redirect('usuarios:perfil')
#
#         return render(request, 'usuarios/login.html', {'error': "Usuario o contraseña incorrectos"})
#
#     return render(request, 'usuarios/login.html')

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    # LoginView redirige automáticamente a settings.LOGIN_REDIRECT_URL


# --- LOGOUT ---

# def logout_view(request):
#     logout(request)
#     return redirect('usuarios:login')

class CustomLogoutView(LogoutView):
    next_page = 'usuarios:login'


# --- REGISTRO ---

# --- CÓDIGO ANTERIOR (FBV) ---
# def registro_view(request):
#     if request.method == "POST":
#         form = RegistroForm(request.POST)
#
#         if form.is_valid():
#             user = User.objects.create_user(
#                 username=form.cleaned_data['username'],
#                 password=form.cleaned_data['password'],
#                 email=form.cleaned_data['email']
#             )
#
#             PerfilUsuario.objects.create(user=user)
#
#             return redirect('usuarios:login')
#
#     else:
#         form = RegistroForm()
#
#     return render(request, 'usuarios/registro.html', {'form': form})

class RegistroView(generic.CreateView):
    form_class = RegistroForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')
    # Nota: La creación del PerfilUsuario se movió al método save() del forms.py


# --- PERFIL ---

# @login_required
# def perfil_view(request):
#     perfil = request.user.perfil
#     compras = request.user.compras.all()
#     return render(request, 'usuarios/perfil.html', {'perfil': perfil, 'compras': compras})

class PerfilView(LoginRequiredMixin, generic.DetailView):
    model = PerfilUsuario
    template_name = 'usuarios/perfil.html'
    context_object_name = 'perfil'

    def get_object(self):
        # Devuelve el perfil del usuario logueado, ignorando la URL
        return self.request.user.perfil

    def get_context_data(self, **kwargs):
        # Inyectamos las compras al contexto
        context = super().get_context_data(**kwargs)
        context['compras'] = self.request.user.compras.all()
        return context


# --- PRODUCTOS --- 

# @login_required
# def productos_view(request):
#     productos = Producto.objects.all()
#     return render(request, 'usuarios/productos.html', {'productos': productos})

class ProductosView(LoginRequiredMixin, generic.ListView):
    model = Producto
    template_name = 'usuarios/productos.html'
    context_object_name = 'productos'


# --- CREAR PRODUCTO ---

# @login_required
# def crear_producto_view(request):
#     # Solo admins pueden crear productos
#     if not request.user.is_staff:
#         return redirect('usuarios:productos')  # o muestra error
#
#     if request.method == "POST":
#         form = ProductoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('usuarios:productos')
#     else:
#         form = ProductoForm()
#
#     return render(request, 'usuarios/crear_producto.html', {'form': form})

class CrearProductoView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'usuarios/crear_producto.html'
    success_url = reverse_lazy('usuarios:productos')

    def test_func(self):
        # Validación de seguridad: solo Staff
        return self.request.user.is_staff


# --- EDITAR PERFIL ---

# @login_required
# def editar_perfil(request):
#     perfil = PerfilUsuario.objects.get(user=request.user)
#
#     if request.method == 'POST':
#         form = EditarPerfilForm(request.POST, instance=perfil, user=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('usuarios:perfil')
#
#     else:
#         form = EditarPerfilForm(instance=perfil, user=request.user)
#
#     return render(request, 'usuarios/editar_perfil.html', {
#         'form': form
#     })

class EditarPerfilView(LoginRequiredMixin, generic.UpdateView):
    model = PerfilUsuario
    form_class = EditarPerfilForm
    template_name = 'usuarios/editar_perfil.html'
    success_url = reverse_lazy('usuarios:perfil')

    def get_object(self):
        # Asegura que edite SU propio perfil
        return self.request.user.perfil

    def get_form_kwargs(self):
        # Pasa el usuario al formulario para editar email/nombre también
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


# --- COMPRAR ---

@login_required
def comprar_view(request):
    # Filtros
    search = request.GET.get("search", "")
    categoria = request.GET.get("categoria", "")

    productos = Producto.objects.filter(activo=True)

    if search:
        productos = productos.filter(nombre__icontains=search)

    if categoria:
        productos = productos.filter(categoria__icontains=categoria)

    # Procesar compra
    if request.method == "POST":
        producto_id = request.POST.get("producto_id")
        cantidad = int(request.POST.get("cantidad", 1))

        # Usamos get_object_or_404 por seguridad (mejora de ing.)
        producto = get_object_or_404(Producto, id=producto_id)

        compra = Compra(
            usuario=request.user,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.costo,
            total=producto.costo * cantidad
        )
        compra.save()
        return redirect("usuarios:perfil")

    # Categorías disponibles
    categorias = Producto.objects.values_list("categoria", flat=True).distinct()

    return render(request, "usuarios/comprar.html", {
        "productos": productos,
        "categorias": categorias,
        "search": search,
        "categoria": categoria
    })