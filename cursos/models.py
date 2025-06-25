from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from curseguridad.storage_backends import MediaStorage
import os

class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=7, decimal_places=2, default=50.00) 
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


def archivo_upload_path(instance, filename):
    return f'cursos/{instance.curso.id}/{filename}'


class ArchivoCurso(models.Model):
    TIPO_CHOICES = [
        ('pptx', 'PowerPoint'),
        ('pdf', 'PDF'),
        ('docx', 'Word'),
        ('otro', 'Otro'),
    ]

    curso = models.ForeignKey(Curso, related_name='archivos', on_delete=models.CASCADE)
    archivo = models.FileField(
        upload_to=archivo_upload_path,
        storage=MediaStorage(),  # Usamos S3 como backend
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro')
    subido_en = models.DateTimeField(auto_now_add=True)

    def clean(self):
        ext = os.path.splitext(self.archivo.name)[1].lower()
        if ext == '.pptx':
            self.tipo = 'pptx'
        elif ext == '.pdf':
            self.tipo = 'pdf'
        elif ext in ['.docx', '.doc']:
            self.tipo = 'docx'
        else:
            self.tipo = 'otro'

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.archivo:
            self.archivo.delete(save=False)
        super().delete(*args, **kwargs)


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pagado = models.BooleanField(default=False)



class CursoComprado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    pagado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'curso')  # evita compras duplicadas

    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo} - {'Pagado' if self.pagado else 'No pagado'}"
