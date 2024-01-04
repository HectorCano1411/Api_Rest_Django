# api/admin.py
from django.contrib import admin
from iniciar.models import NuevoRegistro
from transferencias.models import  Transferencia

class NuevoRegistroAdmin(admin.ModelAdmin):
    list_display = ('rut', 'Nombres', 'Apellidos', 'SaldoContable', 'TipoCuenta', 'Estado')
    search_fields = ('rut', 'Nombres', 'Apellidos')
    list_filter = ('TipoCuenta', 'Estado')


class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('cuenta_origen', 'cuenta_destino', 'monto', 'fecha', 'aprobada')
    search_fields = ('cuenta_origen__rut', 'cuenta_destino__rut', 'monto', 'fecha')
    list_filter = ('aprobada', 'fecha')
