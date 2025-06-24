import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

from django.db import models
from django.core.exceptions import ValidationError
import os


class Presentation(models.Model):
    title = models.CharField(max_length=200)
    pptx_file = models.FileField(
        upload_to='presentations/pptx/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if not self.pptx_file:
            raise ValidationError("Debe subir un archivo PPTX")

        # Verificar extensión del archivo
        ext = os.path.splitext(self.pptx_file.name)[1]
        if ext.lower() != '.pptx':
            raise ValidationError("Solo se permiten archivos PPTX")

    def save(self, *args, **kwargs):
        self.clean()  # Valida antes de guardar
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
    # Elimina el archivo del almacenamiento (S3 o local)
     if self.pptx_file:
        self.pptx_file.delete(save=False)
        super().delete(*args, **kwargs)


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pagado = models.BooleanField(default=False)   
