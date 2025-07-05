from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from curseguridad.storage_backends import MediaStorage
import os
from django.core.validators import RegexValidator


class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=7, decimal_places=2, default=50.00)
    creado_en = models.DateTimeField(auto_now_add=True)
    video = models.FileField(
    upload_to='cursos/videos/',
    storage=MediaStorage(),
    null=True,
    blank=True,
)

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
    
    nombre = models.CharField(max_length=150, blank=True, default='')
    apellido_paterno = models.CharField(max_length=150, blank=True, default='')
    apellido_materno = models.CharField(max_length=150, blank=True, default='')
    
    curp = models.CharField(
        max_length=18,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$',
                message='CURP no tiene un formato válido.'
            )
        ]
    )
    
    puesto = models.CharField(max_length=100)
    ocupacion_especifica = models.CharField(max_length=150, blank=True, default='')
    nombre_razon_social = models.CharField("Nombre o razón social", max_length=200, blank=True, default='')
    refc_empresa = models.CharField("RFC de la empresa", max_length=13, blank=True, default='')

    def __str__(self):
        partes = [self.nombre, self.apellido_paterno, self.apellido_materno]
        nombre_completo = ' '.join(p for p in partes if p).strip()
        return nombre_completo if nombre_completo else self.user.username

    class Meta:
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']

class CursoComprado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    pagado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'curso')  # evita compras duplicadas

    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo} - {'Pagado' if self.pagado else 'No pagado'}"


class Examen(models.Model):
    curso = models.OneToOneField(Curso, on_delete=models.CASCADE, related_name='examen')
    tiempo_minutos = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"Examen de {self.curso.titulo}"

class PreguntaExamen(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField()

    def __str__(self):
        return f"Pregunta: {self.texto[:50]}"

class OpcionRespuesta(models.Model):
    pregunta = models.ForeignKey(PreguntaExamen, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"Opción: {self.texto} - Correcta: {self.es_correcta}"

class IntentoExamen(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    porcentaje = models.FloatField(null=True, blank=True)
    aprobado = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=[('en_curso','En curso'), ('finalizado','Finalizado')], default='en_curso')
    intentos = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Intento de {self.usuario.username} en {self.examen} - Estado: {self.estado}"

class ProgresoCurso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    examen_aprobado = models.BooleanField(default=False)
    intentos = models.IntegerField(default=0)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    certificado = models.FileField(upload_to='certificados/', null=True, blank=True)

    video_visto_completo = models.BooleanField(default=False)  # <-- nuevo campo
    porcentaje_examen = models.FloatField(null=True, blank=True)  # <-- nuevo campo

    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo}"