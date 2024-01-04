# transferencias/admin.py
from django.contrib import admin
from .models import Transferencia

@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('cuenta_origen', 'cuenta_destino', 'monto', 'fecha', 'aprobada')
    search_fields = ('cuenta_origen__Nombres', 'cuenta_destino__Nombres', 'monto')
    list_filter = ('aprobada', 'fecha')
    readonly_fields = ('fecha',)  # Puedes ajustar según tus necesidades
