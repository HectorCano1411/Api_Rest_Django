from django import forms
from .models import Transferencia


class TransferenciaForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = ['cuenta_origen', 'cuenta_destino', 'monto', 'aprobada', 'referencia', 'tasa_interes', 'descripcion']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            'aprobada': forms.CheckboxInput(attrs={'class': 'form-check-input', 'required': True}),
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'tasa_interes': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'style': 'overflow-y: scroll;', 'required': True, 'rows': 3, 'cols': 30}),
        }
    def clean_cuenta_destino(self):
        cuenta_origen = self.cleaned_data['cuenta_origen']
        cuenta_destino = self.cleaned_data['cuenta_destino']

        # Validación: La cuenta de destino no puede ser la misma que la cuenta de origen
        if cuenta_destino == cuenta_origen:
            raise forms.ValidationError("La cuenta de destino no puede ser la misma que la cuenta de origen.")

        return cuenta_destino

    def clean_monto(self):
        monto = self.cleaned_data['monto']

        # Validación: El monto debe ser un valor positivo
        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero.")

        return monto


    def clean_tasa_interes(self):
        tasa_interes = self.cleaned_data['tasa_interes']
        aprobada = self.cleaned_data['aprobada']

        # Validación: Si la transferencia está aprobada, la tasa de interés debe ser mayor que cero
        if aprobada and (tasa_interes is None or tasa_interes <= 0):
            raise forms.ValidationError("Si la transferencia está aprobada, la tasa de interés debe ser mayor que cero.")

        return tasa_interes
