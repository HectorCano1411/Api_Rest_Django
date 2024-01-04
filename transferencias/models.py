
# transferencias/models.py
from django.db import models
from iniciar.models import NuevoRegistro




# transferencias/models.py
from django.db import models
from iniciar.models import NuevoRegistro

class Transferencia(models.Model):
    id = models.AutoField(primary_key=True)
    cuenta_origen = models.ForeignKey(NuevoRegistro, on_delete=models.CASCADE, related_name='transferencias_origen')
    cuenta_destino = models.ForeignKey(NuevoRegistro, on_delete=models.CASCADE, related_name='transferencias_destino')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    aprobada = models.BooleanField(default=False)
    referencia = models.CharField(max_length=20, blank=True, null=True)
    detalles = models.CharField(max_length=20, blank=True, null=True)
    tasa_interes = models.FloatField(blank=True, null=True)
    motivo_rechazo = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Transferencia de {self.cuenta_origen} a {self.cuenta_destino} por ${self.monto}'
