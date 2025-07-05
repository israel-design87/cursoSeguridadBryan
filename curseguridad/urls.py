"""
URL configuration for curseguridad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from cursos import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),

    # Autenticación y pagos
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('', views.root_redirect, name='root'),
    path('signin/', views.signin, name='signin'),
    path('comprar_curso/<int:curso_id>/', views.crear_checkout_por_curso, name='crear_checkout_por_curso'),
    path('pago_exitoso_curso/<int:curso_id>/', views.pago_exitoso_curso, name='pago_exitoso_curso'),
    path('pago_cancelado_curso/<int:curso_id>/', views.pago_cancelado_curso, name='pago_cancelado_curso'),
    path('curso/<int:pk>/', views.detalle_curso, name='detalle_curso'),
    path('curso/<int:curso_id>/examen/', views.examen_curso, name='examen_curso'),
    path('curso/<int:curso_id>/marcar_video/', views.marcar_video_completo, name='marcar_video_completo'),
    path('curso/<int:curso_id>/certificado/', views.certificado_reconocimiento, name='certificado_reconocimiento'),
    path('curso/<int:curso_id>/configurar_examen/', views.crear_editar_examen, name='crear_editar_examen'),
    path('curso/<int:curso_id>/agregar_pregunta/', views.agregar_pregunta, name='agregar_pregunta'),
    path('curso/<int:curso_id>/configurar_examen/', views.configurar_examen, name='configurar_examen'),
    path('usuarios-aprobados/', views.usuarios_aprobados_lista, name='usuarios_aprobados_lista'),



    # CURSOS
    path('cursos/upload/', views.subir_curso, name='subir_curso'),
    path('cursos/<int:pk>/', views.detalle_curso, name='detalle_curso'),
    path('archivo/eliminar/<int:archivo_id>/', views.eliminar_archivo, name='eliminar_archivo'),
    path('curso/eliminar/<int:curso_id>/', views.eliminar_curso, name='eliminar_curso'),


    path('curso/<int:curso_id>/examen/preguntas/', views.listar_preguntas, name='listar_preguntas'),
    path('curso/<int:curso_id>/examen/preguntas/agregar/', views.agregar_pregunta, name='agregar_pregunta'),
    path('curso/<int:curso_id>/examen/preguntas/<int:pregunta_id>/editar/', views.editar_pregunta, name='editar_pregunta'),
    path('examen/preguntas/<int:pregunta_id>/eliminar/', views.eliminar_pregunta, name='eliminar_pregunta'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)