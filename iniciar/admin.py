from django.contrib import admin
from .models import NuevoRegistro ,SecurityAudit # Asegúrate de importar el modelo NuevoRegistro desde tu aplicación

# Register your models here.
class NuevoRegistroAdmin(admin.ModelAdmin):
    list_display = ('rut', 'Nombres', 'Apellidos', 'Estado')  # Cambia "Rut" a "rut"
    list_filter = ('Estado',)  
    search_fields = ('rut', 'Nombres', 'Apellidos') 

admin.site.register(NuevoRegistro, NuevoRegistroAdmin)





class SecurityAuditAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event_type', 'user_details', 'details')
    list_filter = ('event_type',)
    search_fields = ('user__Nombres', 'user__Apellidos', 'event_type', 'details')

    def user_details(self, obj):
        return f'{obj.user.Nombres} {obj.user.Apellidos} ({obj.user.rut})'

    user_details.short_description = 'Usuario'

admin.site.register(SecurityAudit, SecurityAuditAdmin)


# Define una clase personalizada para la administración de NuevoRegistro
