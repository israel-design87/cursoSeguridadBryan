from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Curso

# @receiver(post_save, sender=User)
# def crear_perfil_usuario(sender, instance, created, **kwargs):
#     if created:
#         print(f"✅ Perfil creado para: {instance.username}")
#         PerfilUsuario.objects.create(user=instance) 


@receiver(post_delete, sender=Curso)
def borrar_video_al_eliminar_curso(sender, instance, **kwargs):
    if instance.video:
        instance.video.delete(save=False)