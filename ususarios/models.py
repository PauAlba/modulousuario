from django.db import models

# Create your models here.
from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    direccion = models.TextField(blank=True, null=True)
    rol = models.CharField(max_length=30, choices=[('cliente','Cliente'),('admin','Admin')], default='cliente')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} <{self.email}>"

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Compra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='compras')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='compras')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # precio al momento de compra
    total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
    #para que el total se calcule auto.
    def save(self, *args, **kwargs):
        self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Compra {self.id} - {self.usuario.email} - {self.producto.nombre}"
