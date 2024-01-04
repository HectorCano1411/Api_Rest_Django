# transferencias/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from transferencias.models import Transferencia
from iniciar.models import NuevoRegistro

@receiver(post_save, sender=Transferencia)
def actualizar_saldo_contable(sender, instance, **kwargs):
    cuenta_origen = instance.cuenta_origen
    cuenta_destino = instance.cuenta_destino

    cuenta_origen.SaldoContable -= instance.monto
    cuenta_destino.SaldoContable += instance.monto

    cuenta_origen.save()
    cuenta_destino.save()
