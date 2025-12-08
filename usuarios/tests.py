from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Usuario

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
        self.assertEqual(self.usuario1.correo, 'javier@correo.com')