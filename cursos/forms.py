from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Presentation

class FormularioRegistro(UserCreationForm):

    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de usuario (máx 150 caracteres)'
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña (mínimo 8 caracteres)'
        }),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repite tu contraseña'
        }),
    )

    class Meta:
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminamos el help_text para que no aparezca abajo
        for field in self.fields.values():
            field.help_text = ''


            

class PowerPointUploadForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'pptx_file']
    
    def clean_pptx_file(self):
        pptx_file = self.cleaned_data.get('pptx_file')
        if not pptx_file:
            raise forms.ValidationError("Debe seleccionar un archivo")
        
        ext = pptx_file.name.split('.')[-1].lower()
        if ext != 'pptx':
            raise forms.ValidationError("Solo se permiten archivos .pptx")
        
        return pptx_file