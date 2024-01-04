from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password, check_password
from .models import NuevoRegistro
import re



class RegistroNuevoForm(forms.ModelForm):
    rut = forms.CharField(max_length=12, label='RUT', widget=forms.TextInput(attrs={'placeholder': 'Ej:12345678-9'}))
    clave1 = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    clave2 = forms.CharField(label='Confirmar',widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))    
    Nombres = forms.CharField(max_length=100, label='Nombres')
    Apellidos = forms.CharField(max_length=100, label='Apellidos')
    TipoCuenta = forms.ChoiceField(choices=NuevoRegistro.TIPOS_DE_CUENTA, label='Tipo de Cuenta')

   
    
    class Meta:
        model = NuevoRegistro
        fields = ['rut', 'clave1', 'clave2', 'Nombres', 'Apellidos','TipoCuenta']
        
    def clean_clave1(self):
        clave = self.cleaned_data['clave1']
        if len(clave) > 16:
            raise ValidationError("La contraseña no debe contener más de 16 caracteres.")

        # Validación de complejidad de contraseña
        self.validate_password_complexity(clave)

        return clave

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        # Validación básica del formato del RUT: números y guión
        if not re.match(r'^\d+-\d$', rut):
            raise ValidationError("El RUT no tiene el formato correcto (Ejemplo: 12345678-9).")

        return rut

    def validate_password_complexity(self, password):
        if len(password) < 6:
            raise ValidationError("La contraseña debe tener al menos 6 caracteres.")
        if len(password) > 16:
            raise ValidationError("La contraseña no debe tener más de 16 caracteres.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        if not re.search(r'[0-9]', password):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[!@#$%^&*()_+{}[\]:;<>,.?~\\-]', password):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")

    def save(self, commit=True):
        usuario = super().save(commit=False)
        clave = self.cleaned_data['clave1']

        # Utiliza make_password para encriptar la contraseña
        usuario.clave1 = make_password(clave)

        if commit:
            usuario.save()
        return usuario

class AdminAuthenticationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)