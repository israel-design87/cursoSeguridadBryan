from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import FormularioRegistro
import os
import stripe
from django.conf import settings
from .models import PerfilUsuario
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pptx import Presentation as PPTXPresentation
import os
from django.conf import settings
from django.http import FileResponse
from django.core.exceptions import ObjectDoesNotExist
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Curso, ArchivoCurso
from .forms import CursoForm, ArchivoCursoFormSet
from .models import CursoComprado

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': FormularioRegistro()
        })
    else:
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            try:
                # Crear usuario
                user = User.objects.create_user(username=username, password=password)
                user.save()

                # Autenticar usuario
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)  # Loguear usuario

                return redirect('home')

            except IntegrityError:
                # Usuario ya existe
                return render(request, 'signup.html', {
                    'form': form,
                    'error': 'El usuario ya existe.'
                })
        else:
            return render(request, 'signup.html', {
                'form': form,
                'error': 'Formulario inválido'
            })


def signin(request):

    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorect'
            })
        else:
            login(request, user)
            return redirect('home')


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def convert_pptx_to_pdf(pptx_path, pdf_path):
    ppt = PPTXPresentation(pptx_path)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    for slide in ppt.slides:
        y_position = height - 50  # Margen superior

        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                lines = shape.text.strip().split('\n')
                for line in lines:
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50
                    c.drawString(50, y_position, line)
                    y_position -= 20

        c.showPage()  # Nueva página para siguiente diapositiva

    c.save()

@login_required
def home(request):
    
    # Debug conexión a S3 (opcional)
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print("✅ Conexión S3 exitosa. Objetos encontrados:", response.get('KeyCount', 0))
    except ClientError as e:
        print("❌ Error de conexión con S3:", e)

    if hasattr(default_storage, 'bucket'):
        print("🔍 Archivos en S3 con prefijo 'media/':")
        for obj in default_storage.bucket.objects.filter(Prefix='media/'):
            print(" -", obj.key)

    # Listar cursos ordenados más recientes
    cursos = Curso.objects.all().order_by('-creado_en')
    
    cursos_con_acceso = set(
        CursoComprado.objects.filter(usuario=request.user, pagado=True).values_list('curso_id', flat=True)
    )

    # Renderizar plantilla de cursos
    return render(request, 'home.html', {
        'cursos': cursos,
        'cursos_con_acceso': cursos_con_acceso,
    })

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')
    # Renderizamos el signin con el formulario para no usar redirección 302
    return render(request, 'signin.html', {
        'form': AuthenticationForm()
    })


@login_required
def pago_cancelado_curso(request, curso_id):
    return render(request, 'pago_cancelado.html', {'curso_id': curso_id})


def registro_exitoso(request):
    username = request.session.pop('signup_username', None)
    password = request.session.pop('signup_password', None)

    if username and password:
        try:
            # Crear el usuario (esto activa la señal y crea el perfil)
            user = User.objects.create_user(username=username, password=password)
            login(request, user)

            # Obtener el perfil creado por la señal
            perfil = PerfilUsuario.objects.get(user=user)
            perfil.pagado = True
            perfil.save()

            return redirect('home')
        except IntegrityError:
            return redirect('/signup/?error=usuario_existente')
    else:
        return redirect('/signup/?error=datos_invalidos')


def registro_cancelado(request):
    username = request.session.pop('signup_username', None)
    password = request.session.pop('signup_password', None)

    if username and password:
        try:
            user = User.objects.create_user(username=username, password=password)

            # Obtener el perfil creado por la señal
            perfil = PerfilUsuario.objects.get(user=user)
            perfil.pagado = False  # explícitamente
            perfil.save()
        except IntegrityError:
            return redirect('/signup/?error=usuario_existente')

    return render(request, 'signup.html', {
        'form': FormularioRegistro(),
        'error': 'El pago fue cancelado o fallido. Intenta de nuevo.'
    })

def es_superusuario(user):
    return user.is_superuser


@login_required
def subir_curso(request):
    if request.method == 'POST':
        curso_form = CursoForm(request.POST)
        formset = ArchivoCursoFormSet(request.POST, request.FILES, queryset=ArchivoCurso.objects.none())
        if curso_form.is_valid() and formset.is_valid():
            curso = curso_form.save(commit=False)
            curso.creado_por = request.user
            curso.save()

            for form in formset:
                if form.cleaned_data:
                    archivo = form.save(commit=False)
                    archivo.curso = curso
                    archivo.save()

            return redirect('detalle_curso', pk=curso.id)
    else:
        curso_form = CursoForm()
        formset = ArchivoCursoFormSet(queryset=ArchivoCurso.objects.none())

    return render(request, 'subir_curso.html', {
        'curso_form': curso_form,
        'formset': formset,
    })

@user_passes_test(es_superusuario)
def eliminar_archivo(request, archivo_id):
    archivo = get_object_or_404(ArchivoCurso, id=archivo_id)
    curso_id = archivo.curso.id
    archivo.delete()
    return redirect('detalle_curso', pk=curso_id)


@user_passes_test(es_superusuario)
def eliminar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    # Ejecuta el delete personalizado de cada archivo
    for archivo in curso.archivos.all():
        archivo.delete()

    # Luego elimina el curso
    curso.delete()

    return redirect('home')

@login_required
def crear_checkout_por_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    # Guardar en metadata para luego asociar
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'mxn',
                'product_data': {
                    'name': curso.titulo,
                },
                'unit_amount': int(curso.precio * 100),  # en centavos
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/pago_exitoso_curso/{curso.id}/'),
        cancel_url=request.build_absolute_uri(f'/pago_cancelado_curso/{curso.id}/'),
        metadata={
            'user_id': request.user.id,
            'curso_id': curso.id,
        }
    )
    return redirect(session.url, code=303)


@login_required
def pago_exitoso_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    obj, creado = CursoComprado.objects.get_or_create(
        usuario=request.user,
        curso=curso
    )
    obj.pagado = True
    obj.save()
    return redirect('detalle_curso', pk=curso.id)

@login_required
def detalle_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)

    # Verificación de pago para usuarios normales
    if not request.user.is_superuser:
        try:
            compra = CursoComprado.objects.get(usuario=request.user, curso=curso)
            if not compra.pagado:
                return redirect('crear_checkout_por_curso', curso_id=pk)
        except CursoComprado.DoesNotExist:
            return redirect('crear_checkout_por_curso', curso_id=pk)

    # Mostrar archivos del curso
    archivos = ArchivoCurso.objects.filter(curso=curso)

    # Superusuario puede subir más archivos
    if request.method == 'POST' and request.user.is_superuser:
        formset = ArchivoCursoFormSet(request.POST, request.FILES, queryset=ArchivoCurso.objects.none())
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    archivo = form.save(commit=False)
                    archivo.curso = curso
                    archivo.save()
            return redirect('detalle_curso', pk=pk)
    else:
        formset = ArchivoCursoFormSet(queryset=ArchivoCurso.objects.none()) if request.user.is_superuser else None

    return render(request, 'detalle_curso.html', {
        'curso': curso,
        'archivos': archivos,
        'formset': formset,
    })
