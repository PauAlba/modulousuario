from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import PerfilUsuario, Producto, Compra

class BaseTestCase(TestCase):
    def setUp(self):
        # Creamos un usuario base y su perfil
        self.user = User.objects.create_user(
            username='TestUser', 
            email='test@correo.com', 
            password='password123'
        )
        # Nota: Dependiendo de tus signals, el perfil se crea auto o manual.
        # Aquí lo aseguramos:
        self.perfil, _ = PerfilUsuario.objects.get_or_create(user=self.user)
        self.perfil.direccion = "Calle Prueba"
        self.perfil.save()

# PRUEBA 1: Registro
class RegistroTestCase(TestCase):
    def setUp(self):
        # Usamos el namespace 'usuarios:'
        self.url = reverse('usuarios:registro')

    def test_acceso_registro(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_registro_exitoso(self):
        # Tu vista usa UserCreationForm o similar, enviamos datos de User
        data = {
            'username': 'NuevoUsuario',
            'email': 'nuevo@correo.com',
            'password': 'password123',
            'confirm_password': 'password123', # A veces requerido por forms de Django
            # Si tu RegistroForm pide dirección, agrégala aquí:
            'direccion': 'Calle Nueva' 
        }
        # Nota: Si tu form valida password confirmation, esto podría variar.
        # Asumimos registro estándar.
        response = self.client.post(self.url, data)
        
        # Si es exitoso, redirige al login (status 302)
        if response.status_code == 200:
            # Si falla, imprimimos errores del form para depurar
            print(response.context['form'].errors)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='NuevoUsuario').exists())

# PRUEBA 2: Perfil (Requiere Login)
class PerfilTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('usuarios:perfil')

    def test_perfil_sin_login(self):
        # Debe redirigir al login
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)

    def test_perfil_con_login(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['perfil'], self.perfil)

# PRUEBA 3: Editar Perfil (Sin ID en URL)
class EditarPerfilTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('usuarios:editar_perfil') # Sin argumentos
        self.client.force_login(self.user)

    def test_editar_perfil(self):
        # Tu vista EditarPerfilView usa UpdateView con un form que recibe 'user'.
        # Enviamos datos para actualizar PerfilUsuario y User
        data = {
            'first_name': 'Nombre Editado', # Campo de User
            'email': 'editado@correo.com',  # Campo de User
            'direccion': 'Direccion Editada' # Campo de PerfilUsuario
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 302) # Redirección a perfil
        
        self.user.refresh_from_db()
        self.perfil.refresh_from_db()
        
        # Verificamos que se guardó (depende de tu form qué campos guarda)
        self.assertEqual(self.perfil.direccion, 'Direccion Editada')

# PRUEBA 4: Crear Producto (Solo Admin)
class ProductoTestCase(TestCase):
    def setUp(self):
        self.url_crear = reverse('usuarios:crear_producto')
        self.url_lista = reverse('usuarios:productos')
        
        # Usuario normal
        self.user_normal = User.objects.create_user('normal', 'n@n.com', '123')
        # Usuario Staff (Admin)
        self.user_admin = User.objects.create_user('admin', 'a@a.com', '123', is_staff=True)

    def test_crear_producto_permiso_denegado(self):
        self.client.force_login(self.user_normal)
        response = self.client.get(self.url_crear)
        # UserPassesTestMixin suele dar 403 Forbidden o redirigir login
        self.assertIn(response.status_code, [403, 302]) 

    def test_crear_producto_exitoso(self):
        self.client.force_login(self.user_admin)
        data = {
            'nombre': 'Laptop Gamer',
            'costo': 15000.00,
            'categoria': 'Tecnología',
            'descripcion': 'Muy rápida'
        }
        response = self.client.post(self.url_crear, data)
        
        self.assertEqual(response.status_code, 302) # Redirige a lista
        self.assertTrue(Producto.objects.filter(nombre='Laptop Gamer').exists())

# PRUEBA 5: Comprar (ID en POST, no en URL)
class ComprarTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('usuarios:comprar')
        self.client.force_login(self.user)
        
        # Creamos producto para comprar
        self.producto = Producto.objects.create(
            nombre="Coca Cola",
            costo=20.00,
            categoria="Bebidas",
            activo=True
        )

    def test_realizar_compra(self):
        # Tu vista busca 'producto_id' y 'cantidad' en el POST
        data = {
            'producto_id': self.producto.id,
            'cantidad': 3
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 302) # Redirige a perfil
        
        # Verificar que se creó la compra
        compra = Compra.objects.filter(usuario=self.user, producto=self.producto).first()
        self.assertIsNotNone(compra)
        self.assertEqual(compra.cantidad, 3)
        self.assertEqual(compra.total, 60.00) # 20 * 3

    def test_busqueda_productos(self):
        # La vista de comprar también sirve para buscar (GET)
        response = self.client.get(self.url, {'search': 'Coca'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coca Cola")