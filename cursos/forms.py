from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Curso, ArchivoCurso,Examen
from django import forms
from .models import PreguntaExamen, OpcionRespuesta
from django.forms import inlineformset_factory
from .models import PerfilUsuario

class FormularioRegistro(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario (máx 150 caracteres)'})
    )
    nombre = forms.CharField(
        label="Nombre",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre'})
    )
    apellido_paterno = forms.CharField(
        label="Primer Apellido",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Primer Apellido'})
    )
    apellido_materno = forms.CharField(
        label="Segundo Apellido",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Segundo Apellido'})
    )
    curp = forms.CharField(
        label="CURP",
        max_length=18,
        widget=forms.TextInput(attrs={'placeholder': 'CURP (18 caracteres)'})
    )
    puesto = forms.CharField(
        label="Puesto",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Oficial Plomero'})
    )
    ocupacion_especifica = forms.CharField(
        label="Ocupación específica",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Instalador de tuberías de gas'})
    )
    nombre_razon_social = forms.CharField(
        label="Nombre o razón social de la empresa",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Constructora XYZ S.A. de C.V.'})
    )
    refc_empresa = forms.CharField(
        label="RFC de la empresa",
        max_length=13,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. COX830101ABC'})
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña (mínimo 8 caracteres)'}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite tu contraseña'}),
    )

    class Meta:
        model = User
        fields = (
            "username", "password1", "password2",
            "nombre", "apellido_paterno", "apellido_materno",
            "curp", "puesto", "ocupacion_especifica",
            "nombre_razon_social", "refc_empresa"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''

    def save(self, commit=True):
        user = super().save(commit)
        PerfilUsuario.objects.create(
            user=user,
            nombre=self.cleaned_data['nombre'],
            apellido_paterno=self.cleaned_data['apellido_paterno'],
            apellido_materno=self.cleaned_data['apellido_materno'],
            curp=self.cleaned_data['curp'],
            puesto=self.cleaned_data['puesto'],
            ocupacion_especifica=self.cleaned_data['ocupacion_especifica'],
            nombre_razon_social=self.cleaned_data['nombre_razon_social'],
            refc_empresa=self.cleaned_data['refc_empresa']
        )
        return user


# FORMULARIO PARA CURSOS
class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['titulo', 'descripcion', 'precio', 'video']  # aquí agregas video




# FORMULARIO PARA SUBIDA DE ARCHIVOS
class ArchivoCursoForm(forms.ModelForm):
    class Meta:
        model = ArchivoCurso
        fields = ['archivo']  # tipo se detecta automáticamente en el modelo

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if not archivo:
            raise forms.ValidationError("Debe seleccionar un archivo")
        
        ext = archivo.name.split('.')[-1].lower()
        if ext not in ['pptx', 'pdf', 'docx']:
            raise forms.ValidationError("Formato no permitido. Solo .pptx, .pdf, .docx")
        
        return archivo


# FORMSET para múltiples archivos
ArchivoCursoFormSet = forms.modelformset_factory(
    ArchivoCurso,
    form=ArchivoCursoForm,
    extra=3,  # puedes cambiar a más formularios si lo deseas
    can_delete=False
)


class PreguntaExamenForm(forms.ModelForm):
    class Meta:
        model = PreguntaExamen
        fields = ['texto']

class OpcionRespuestaForm(forms.ModelForm):
    class Meta:
        model = OpcionRespuesta
        fields = ['texto', 'es_correcta']

OpcionFormSet = inlineformset_factory(
    PreguntaExamen,
    OpcionRespuesta,
    form=OpcionRespuestaForm,
    extra=2,
    can_delete=True
)

PreguntaFormSet = inlineformset_factory(
    Examen,
    PreguntaExamen,
    form=PreguntaExamenForm,
    extra=1,
    can_delete=True
)

OpcionRespuestaFormSet = inlineformset_factory(
    PreguntaExamen,
    OpcionRespuesta,
    fields=('texto', 'es_correcta'),
    extra=3,
    can_delete=True,
    widgets={
        'texto': forms.TextInput(attrs={'class': 'form-control'}),
        'es_correcta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)


class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['tiempo_minutos']