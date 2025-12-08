from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import EditarPerfilForm, RegistroForm, PerfilForm, CompraForm, ProductoForm
from .models import PerfilUsuario, Producto, Compra


# LOGIN

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('usuarios:perfil')

        return render(request, 'usuarios/login.html', {'error': "Usuario o contraseña incorrectos"})

    return render(request, 'usuarios/login.html')



# LOGOUT

def logout_view(request):
    logout(request)
    return redirect('usuarios:login')



# REGISTRO

def registro_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email']
            )

            PerfilUsuario.objects.create(user=user)

            return redirect('usuarios:login')

    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})



# PERFIL

@login_required
def perfil_view(request):
    perfil = request.user.perfil
    compras = request.user.compras.all()
    return render(request, 'usuarios/perfil.html', {'perfil': perfil, 'compras': compras})



# PRODUCTOS

@login_required
def productos_view(request):
    productos = Producto.objects.all()
    return render(request, 'usuarios/productos.html', {'productos': productos})


@login_required
def crear_producto_view(request):
    # Solo admins pueden crear productos
    if not request.user.is_staff:
        return redirect('usuarios:productos')  # o muestra error

    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios:productos')
    else:
        form = ProductoForm()

    return render(request, 'usuarios/crear_producto.html', {'form': form})


# COMPRAR

@login_required
def comprar_view(request):
    if request.method == "POST":
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save(commit=False)
            compra.usuario = request.user
            compra.precio_unitario = compra.producto.costo
            compra.save()
            return redirect('usuarios:perfil')
    else:
        form = CompraForm()

    return render(request, 'usuarios/comprar.html', {'form': form})


@login_required
def editar_perfil(request):
    perfil = PerfilUsuario.objects.get(user=request.user)

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=perfil, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('usuarios:perfil')

    else:
        form = EditarPerfilForm(instance=perfil, user=request.user)

    return render(request, 'usuarios/editar_perfil.html', {
        'form': form
    })