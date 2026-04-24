from django.db import models
from django.contrib.auth.models import User


class Tema(models.Model):

    numero_tema = models.IntegerField(unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    orden = models.IntegerField()
    es_activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class UserProfile(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    fecha_nacimiento = models.DateField(null=True, blank=True)

    genero = models.CharField(
        max_length=1,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino')
        ],
        null=True,
        blank=True
    )

    nombre_tutor = models.CharField(max_length=100, null=True, blank=True)

    email_tutor = models.EmailField(null=True, blank=True)

    pais = models.CharField(max_length=50, null=True, blank=True)

    acepto_terminos = models.BooleanField(default=False)
    acepto_terminos_en = models.DateTimeField(null=True, blank=True)
    consentimiento_tutor = models.BooleanField(default=False)
    consentimiento_tutor_en = models.DateTimeField(null=True, blank=True)
    registro_ip = models.GenericIPAddressField(null=True, blank=True)

    ultimo_tema_desbloqueado = models.PositiveSmallIntegerField(default=1)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.usuario.username