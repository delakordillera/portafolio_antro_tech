from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Habilidad, Perfil

class PerfilForm(forms.ModelForm):
    """
    Formulario para que el vecino construya su identidad narrativa.
    """
    class Meta:
        model = Perfil
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Cuéntale a la comunidad quién eres y en qué puedes ayudar...',
                'rows': 3
            }),
        }

class HabilidadForm(forms.ModelForm):
    class Meta:
        model = Habilidad
        # ACTUALIZACIÓN: Incluimos 'imagen' en la lista de campos
        fields = ['titulo', 'descripcion', 'categoria', 'imagen'] 
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Taller de Carpintería'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Describe brevemente qué ofreces...'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Oficios, Educación, Cuidados'
            }),
            # NUEVO WIDGET: Estilo para el campo de subida de archivos
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email