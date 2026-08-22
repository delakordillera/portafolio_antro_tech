import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .models import Habilidad, Perfil

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
MAX_IMAGE_SIZE = 2 * 1024 * 1024
MAX_BIO_LENGTH = 1000
MAX_TITULO_LENGTH = 100
MAX_DESCRIPCION_LENGTH = 2000
MAX_CATEGORIA_LENGTH = 50


def validate_image_file(file):
    if file.size > MAX_IMAGE_SIZE:
        raise forms.ValidationError(f'La imagen no puede superar {MAX_IMAGE_SIZE // (1024*1024)} MB.')
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
        raise forms.ValidationError('Formato no permitido. Usa JPG, PNG, WebP o GIF.')


class HoneypotMixin:
    """
    Campo oculto que los bots rellenan pero los humanos no.
    El campo tiene un nombre atractivo para bots (ej: 'url_website').
    """
    honeypot_field = 'url_website'

    def clean_honeypot(self):
        val = self.cleaned_data.get(self.honeypot_field, '')
        if val:
            raise forms.ValidationError('Spam detectado.')
        return val


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Cuéntale a la comunidad quién eres y en qué puedes ayudar...',
                'rows': 3,
                'maxlength': str(MAX_BIO_LENGTH),
            }),
        }

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '').strip()
        if len(bio) > MAX_BIO_LENGTH:
            raise forms.ValidationError(f'Máximo {MAX_BIO_LENGTH} caracteres.')
        return bio


class HabilidadForm(HoneypotMixin, forms.ModelForm):
    url_website = forms.CharField(
        required=False,
        label='',
        widget=forms.HiddenInput(attrs={'tabindex': '-1', 'autocomplete': 'off'})
    )

    class Meta:
        model = Habilidad
        fields = ['titulo', 'descripcion', 'categoria', 'imagen']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Taller de Carpintería',
                'maxlength': str(MAX_TITULO_LENGTH),
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe brevemente qué ofreces...',
                'maxlength': str(MAX_DESCRIPCION_LENGTH),
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Oficios, Educación, Cuidados',
                'maxlength': str(MAX_CATEGORIA_LENGTH),
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_titulo(self):
        val = self.cleaned_data.get('titulo', '').strip()
        if len(val) < 3:
            raise forms.ValidationError('El título debe tener al menos 3 caracteres.')
        return val

    def clean_descripcion(self):
        val = self.cleaned_data.get('descripcion', '').strip()
        if len(val) < 10:
            raise forms.ValidationError('La descripción debe tener al menos 10 caracteres.')
        return val

    def clean_categoria(self):
        val = self.cleaned_data.get('categoria', '').strip()
        if len(val) < 2:
            raise forms.ValidationError('La categoría debe tener al menos 2 caracteres.')
        return val

    def clean_imagen(self):
        img = self.cleaned_data.get('imagen')
        if img:
            validate_image_file(img)
        return img


class RegistroForm(HoneypotMixin, UserCreationForm):
    url_website = forms.CharField(
        required=False,
        label='',
        widget=forms.HiddenInput(attrs={'tabindex': '-1', 'autocomplete': 'off'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if len(username) < 3:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        if not username.isalnum():
            raise forms.ValidationError('El nombre de usuario solo puede contener letras y números.')
        return username


class LoginForm(HoneypotMixin, forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    url_website = forms.CharField(
        required=False,
        label='',
        widget=forms.HiddenInput(attrs={'tabindex': '-1', 'autocomplete': 'off'})
    )
