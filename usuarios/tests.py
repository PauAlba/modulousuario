from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import PerfilUsuario, Producto, Compra

class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUser', 
            email='test@correo.com', 
            password='password123'
        )
        self.perfil, _ = PerfilUsuario.objects.get_or_create(user=self.user)
        self.perfil.direccion = "Calle Prueba"
        self.perfil.save()

# PRUEBA 1: Registro
class RegistroTestCase(TestCase):
    def setUp(self):
        self.url = reverse('usuarios:registro')

    def test_acceso_registro(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_registro_exitoso(self):
        data = {
            'username': 'NuevoUsuario',
            'email': 'nuevo@correo.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'direccion': 'Calle Nueva' 
        }
        response = self.client.post(self.url, data)
        
        if response.status_code == 200:
            print(response.context['form'].errors)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='NuevoUsuario').exists())

# PRUEBA 2: Perfil (Requiere Login)
class PerfilTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('usuarios:perfil')

    def test_perfil_sin_login(self):
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
        self.url = reverse('usuarios:editar_perfil')
        self.client.force_login(self.user)

    def test_editar_perfil(self):
        data = {
            'first_name': 'Nombre Editado',
            'email': 'editado@correo.com',
            'direccion': 'Direccion Editada'
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 302)
        
        self.user.refresh_from_db()
        self.perfil.refresh_from_db()
        
        self.assertEqual(self.perfil.direccion, 'Direccion Editada')

# PRUEBA 4: Crear Producto (Solo Admin)
class ProductoTestCase(TestCase):
    def setUp(self):
        self.url_crear = reverse('usuarios:crear_producto')
        self.url_lista = reverse('usuarios:productos')
        
        self.user_normal = User.objects.create_user('normal', 'n@n.com', '123')
        self.user_admin = User.objects.create_user('admin', 'a@a.com', '123', is_staff=True)

    def test_crear_producto_permiso_denegado(self):
        self.client.force_login(self.user_normal)
        response = self.client.get(self.url_crear)
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
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(nombre='Laptop Gamer').exists())

# PRUEBA 5: Comprar (ID en POST, no en URL)
class ComprarTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('usuarios:comprar')
        self.client.force_login(self.user)
        
        self.producto = Producto.objects.create(
            nombre="Coca Cola",
            costo=20.00,
            categoria="Bebidas",
            activo=True
        )

    def test_realizar_compra(self):
        data = {
            'producto_id': self.producto.id,
            'cantidad': 3
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 302)
        
        compra = Compra.objects.filter(usuario=self.user, producto=self.producto).first()
        self.assertIsNotNone(compra)
        self.assertEqual(compra.cantidad, 3)
        self.assertEqual(compra.total, 60.00)

    def test_busqueda_productos(self):
        response = self.client.get(self.url, {'search': 'Coca'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coca Cola")