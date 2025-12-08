from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Usuario
from .models import Producto
from .models import Compra

# Create your tests here.

def crear_usuario(username, correo):
    return Usuario.objects.create(
        nombre=username, 
        correo=correo,
        telefono='1234567890',
        direccion='Calle Falsa 123',
        contraseña='12345'
    )

#PRUEBAS A = Registro de Usuario

class RegistroUsuarioTestCase(TestCase):
    def setUp(self):
        self.url_registro = reverse('registro_usuario')
        self.existente = crear_usuario("Prueba", "prueba@correo.com")

    def test_registro_usuario_nuevo(self):
        response = self.client.post(self.url_registro, {
            'nombre': 'Frida',
            'correo': 'frida@correo.com',
            'telefono': '1234567890',
            'direccion': 'Algo',
            'contraseña': '1234'
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(Usuario.objects.filter(correo = 'frida@correo.com').exists())
        nuevo = Usuario.objects.get(correo = 'frida@correo.com')
        self.assertEqual(nuevo.nombre, 'Frida')

    def test_registro_fallido_correo_existente(self):
        response = self.client.post(self.url_registro, {
            'nombre': 'Pau',
            'correo': 'prueba@correo.com',
            'telefono': '0987654321',
            'direccion': 'Otra Calle',
            'contraseña': '54321'
        })

        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, "ya existe", status_code=200) 
        self.assertEqual(Usuario.objects.filter(correo= 'prueba@correo.com').count(), 1)  

#PRUEBAS B = Modificación de Usuario    
class ModificarUsuarioTestCase(TestCase):
    def setUp(self):
        self.usuario1 = crear_usuario("Javier", "javier@correo.com")
        self.usuario2 = crear_usuario("Edgar", "edgar@correo.com")

        self.url_modificar1 = reverse('modificar_usuario', args=[self.usuario1.id])
        self.url_modificar2 = reverse('modificar_usuario', args=[self.usuario2.id])
    
    def test_modificar_usuario_correctamente(self):
        response = self.client.post(self.url_modificar1, {
            'nombre': 'Javier Modificado',
            'correo': 'javier@correo.com',
            'telefono': '1112223333',
            'direccion': 'Calle Nueva 456',
            'contraseña': 'new'
        })

        self.usuario1.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.usuario1.nombre, 'Javier Modificado')
        self.assertEqual(self.usuario1.telefono, '1112223333')

    def test_modificacion_fallida_por_correo_duplicado(self):
        response = self.client.post(self.url_modificar2, {
            'nombre': 'Juan Pablo',
            'correo': 'edgar@correo.com',
            'telefono': '4445556666',
            'direccion': 'dupli',
            'contraseña': 'dup'
        })
        self.usuario1.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ya existe este correo")
        self.assertEqual(self.usuario2.correo, 'edgar@correo.com')

#PRUEBAS C = Eliminación de Usuario
class EliminarUsuarioTestCase(TestCase):
    def setUp(self):
        self.usuario = crear_usuario("Juan Pablo", "jp@correo.com")
        self.url_eliminar = reverse('eliminar_usuario', args=[self.usuario.id])

    def test_eliminar_usuario_correctamente(self):
        response = self.client.post(self.url_eliminar)
        self.assertEqual(response.status_code, 302)  
        self.assertFalse(Usuario.objects.filter(id=self.usuario.id).exists())
        self.assertEqual(Usuario.objects.count(), 0)

    def test_eliminacion_usuario_inexistente(self):
        url_inexistente = reverse('eliminar_usuario', args=[9999])  
        response = self.client.post(url_inexistente)
        self.assertEqual(response.status_code, 404)  
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertTrue(Usuario.objects.filter(correo="jp@correo.com").exists())

#PRUEBAS D = Validaciones del Modelo Usuario
class ValidacionesModeloTestCase(TestCase):
    def test_usuario_sin_nombre(self):
        usuario = Usuario(
            nombre="",
            correo="test@correo.com",
            telefono="1231231234",
            direccion="Calle 1",
            contraseña="1234"
        )

        with self.assertRaises(Exception):
            usuario.save()

        self.assertEqual(Usuario.objects.count(), 0)

    def test_correo_invalido(self):
        usuario = Usuario(
            nombre="Prueba",
            correo="correo-sin-arroba",
            telefono="1112223333",
            direccion="N/A",
            contraseña="xx"
        )

        with self.assertRaises(Exception):
            usuario.save()

        self.assertFalse(Usuario.objects.exists())

#PRUEBAS E = Listado de Usuarios
class ListaUsuariosTestCase(TestCase):
    def setUp(self):
        self.u1 = crear_usuario("Ana", "ana@correo.com")
        self.u2 = crear_usuario("Luis", "luis@correo.com")
        self.url_lista = reverse('lista_usuarios')

    def test_listado_correcto(self):
        response = self.client.get(self.url_lista)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana")
        self.assertContains(response, "Luis")


    def test_listado_vacio(self):
        Usuario.objects.all().delete()  

        response = self.client.get(self.url_lista)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay usuarios registrados")
        self.assertEqual(Usuario.objects.count(), 0)

#PRUEBAS F = Seguridad
class SeguridadTestCase(TestCase):
    def setUp(self):
        self.url_registro = reverse('registro_usuario')

    def test_registro_sin_contraseña(self):
        response = self.client.post(self.url_registro, {
            'nombre': 'Frida',
            'correo': 'prueba@correo.com',
            'telefono': '1234567890',
            'direccion': 'Calle 1',
            'contraseña': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La contraseña es obligatoria")
        self.assertFalse(Usuario.objects.filter(correo='prueba@correo.com').exists())

    def test_correo_demasiado_largo(self):
        correo_largo = "a" * 300 + "@correo.com"  
        
        response = self.client.post(self.url_registro, {
            'nombre': 'Test',
            'correo': correo_largo,
            'telefono': '111222333',
            'direccion': 'Hola',
            'contraseña': '111'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "correo no válido")
        self.assertFalse(Usuario.objects.filter(correo=correo_largo).exists())

#PRUEBAS G = Accesso a vistas protegidas
class AccesoViewsTestCase(TestCase):
    def setUp(self):
        self.url_modificar = reverse('modificar_usuario', args=[1])

    def test_acceso_no_autenticado(self):
        response = self.client.get(self.url_modificar)

        self.assertIn(response.status_code, [302, 401, 403])
        self.assertTrue(response.url.startswith("/login"))

    def test_acceso_autenticado(self):
        user = User.objects.create_user(username='test', password='1234')
        self.client.login(username='test', password='1234')

        usuario = crear_usuario("Test", "test@correo.com")
        url = reverse('modificar_usuario', args=[usuario.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, usuario.nombre)

#PRUEBAS H = Agregar Productos
class AgregarProductoTestCase(TestCase):

    def test_agregar_producto_valido(self):
        response = self.client.post(reverse('agregar_producto'), {
            'nombre': 'Camisa',
            'precio': 250,
            'stock': 15
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(nombre='Camisa').exists())
        producto = Producto.objects.get(nombre='Camisa')
        self.assertEqual(producto.stock, 15)

    def test_no_agregar_producto_sin_nombre(self):
        response = self.client.post(reverse('agregar_producto'), {
            'nombre': '',
            'precio': 100,
            'stock': 5
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El nombre es obligatorio")
        self.assertEqual(Producto.objects.count(), 0)

    def test_no_agregar_producto_precio_negativo(self):
        response = self.client.post(reverse('agregar_producto'), {
            'nombre': 'Zapatos',
            'precio': -50,
            'stock': 5
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Precio no válido")
        self.assertFalse(Producto.objects.filter(nombre='Zapatos').exists())

#PRUEBAS I = Realizar Compras
class RealizarCompraTestCase(TestCase):

    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Café",
            precio=50,
            stock=10
        )
        self.url_compra = reverse('realizar_compra', args=[self.producto.id])

    def test_compra_exitosa(self):
        response = self.client.post(self.url_compra, {
            'cantidad': 3
        })

        self.producto.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.producto.stock, 7)  
        self.assertTrue(Compra.objects.filter(producto=self.producto, cantidad=3).exists())

    def test_compra_stock_insuficiente(self):
        response = self.client.post(self.url_compra, {
            'cantidad': 20  
        })

        self.producto.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stock insuficiente")
        self.assertEqual(self.producto.stock, 10)  
        self.assertEqual(Compra.objects.count(), 0)

    def test_compra_cantidad_invalida(self):
        response = self.client.post(self.url_compra, {
            'cantidad': 0
        })

        self.producto.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cantidad no válida")
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(Compra.objects.count(), 0)

    def test_crea_registro_compra(self):
        response = self.client.post(self.url_compra, {
            'cantidad': 1
        })

        self.assertEqual(response.status_code, 302)
        compra = Compra.objects.first()

        self.assertIsNotNone(compra)
        self.assertEqual(compra.producto, self.producto)
        self.assertEqual(compra.cantidad, 1)


