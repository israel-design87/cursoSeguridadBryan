from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Curso, ArchivoCurso

class FormularioRegistro(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario (máx 150 caracteres)'})
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
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''


# FORMULARIO PARA CURSOS
class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['titulo', 'descripcion', 'precio']  # asegúrate de incluirlo



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