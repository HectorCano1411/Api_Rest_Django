from django.db import models
from django.db import models
from django.db.models import Max



class NuevoRegistro(models.Model):
    CUENTA_CORRIENTE = 'corriente'
    CUENTA_AHORRO = 'ahorro'

    TIPOS_DE_CUENTA = [
        (CUENTA_CORRIENTE, 'Cuenta Corriente'),
        (CUENTA_AHORRO, 'Cuenta de Ahorro'),
    ]
    id = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True)
    Nombres = models.CharField(max_length=100)
    Apellidos = models.CharField(max_length=100)
    Clave = models.CharField(max_length=128)
    NumeroCuenta = models.CharField(max_length=20, null=True, blank=True)
    SaldoContable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    TipoCuenta = models.CharField(max_length=10, choices=TIPOS_DE_CUENTA, default=CUENTA_CORRIENTE)
    SaldoCuentaCorriente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SaldoLineaCredito = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    TotalCargos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    TotalAbonos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    Estado = models.BooleanField(default=True)
    intentos_fallidos = models.PositiveIntegerField(default=0)


    def save(self, *args, **kwargs):
        if not self.NumeroCuenta:
            # Obtén el número máximo de cuenta existente
            max_numero_cuenta = NuevoRegistro.objects.all().aggregate(Max('NumeroCuenta'))['NumeroCuenta__max']

            # Si no hay cuentas existentes, comienza desde 1, de lo contrario, incrementa el número
            if max_numero_cuenta is not None:
                self.NumeroCuenta = str(int(max_numero_cuenta) + 1)
            else:
                self.NumeroCuenta = '1'

        super(NuevoRegistro, self).save(*args, **kwargs)


    def __str__(self):
        return f'Usuario: {self.id} {self.Nombres} {self.rut} '


class SecurityAudit(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(NuevoRegistro, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    details = models.TextField()

    def __str__(self):
        return f'{self.timestamp} - {self.user.Nombres} {self.user.Apellidos} - {self.event_type}'

    def create_security_audit(self, event_type, details):
        # Crea un registro de auditoría cuando se llama a este método
        SecurityAudit.objects.create(
            user=self.user,  # Asocia el usuario actual al registro de auditoría
            event_type=event_type,
            details=details
        )

    def save(self, *args, **kwargs):
        # Antes de guardar el objeto SecurityAudit, verifica si hay cambios en el campo Estado
        if self.pk:
            original_obj = SecurityAudit.objects.get(pk=self.pk)
            if original_obj.user.Estado != self.user.Estado:
                # Si el campo Estado ha cambiado, crea un registro de auditoría
                event_type = 'Cambio de Estado'
                details = f'Estado cambiado de {original_obj.user.Estado} a {self.user.Estado}'
                self.create_security_audit(event_type, details)
        super().save(*args, **kwargs)