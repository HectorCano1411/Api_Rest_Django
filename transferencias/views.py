# transferencias/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .forms import TransferenciaForm
from .models import Transferencia
from iniciar.models import NuevoRegistro
from django.db.models import F
from datetime import datetime, timedelta
from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.db import transaction


# def crear_transferencia(request):
#     if request.method == 'POST':
#         form = TransferenciaForm(request.POST)
#         if form.is_valid():
#             transferencia = form.save(commit=False)
            
            
#             # Actualizar saldos de cuentas
#             cuenta_origen = transferencia.cuenta_origen
#             cuenta_destino = transferencia.cuenta_destino

#             if cuenta_origen.SaldoContable >= transferencia.monto:
#                 cuenta_origen.SaldoContable = F('SaldoContable') - transferencia.monto
#                 cuenta_destino.SaldoContable = F('SaldoContable') + transferencia.monto

#                 # Convertir los campos Decimal a float antes de serializar a JSON
#                 transferencia.detalles = json.dumps({
#                     'monto': float(transferencia.monto),
                    
#                     # Agrega otros campos aquí...
#                 })

#                 transferencia.aprobada = True
#                 transferencia.save()

#                 cuenta_origen.save()
#                 cuenta_destino.save()

#                 # Puedes redirigir a una página de éxito o a cualquier otra vista después de guardar la transferencia
#                 return redirect('aprobar_transferencia', transferencia.id)
#             else:
#                 # Manejar el caso en que no hay saldo suficiente en la cuenta de origen
#                 form.add_error(None, 'Saldo insuficiente en la cuenta de origen.')
#     else:
#         form = TransferenciaForm()
#         form.fields['cuenta_origen'].queryset = NuevoRegistro.objects.all()
#         form.fields['cuenta_destino'].queryset = NuevoRegistro.objects.all()

#     return render(request, 'transferencia_form.html', {'form': form})
# Otras vistas se mantienen similares, pero con ajustes para trabajar con el nuevo modelo de Cuenta y Transferencia.
@transaction.atomic
def crear_transferencia(request):
    if request.method == 'POST':
        form = TransferenciaForm(request.POST)
        if form.is_valid():
            transferencia = form.save(commit=False)
            
            # Actualizar saldos de cuentas
            cuenta_origen = transferencia.cuenta_origen
            cuenta_destino = transferencia.cuenta_destino

            if cuenta_origen.SaldoContable >= transferencia.monto:
                cuenta_origen.SaldoContable = F('SaldoContable') - transferencia.monto
                cuenta_destino.SaldoContable = F('SaldoContable') + transferencia.monto

                # Utiliza el codificador JSON de Django para serializar campos específicos a JSON
                transferencia.detalles = json.dumps({
                    'monto': float(transferencia.monto),
                }, cls=DjangoJSONEncoder)  # Usa DjangoJSONEncoder

                transferencia.aprobada = True
                transferencia.save()

                cuenta_origen.save()
                cuenta_destino.save()
                messages.success(request, 'Transferencia realizada con éxito.')


                # Puedes redirigir a una página de éxito o a cualquier otra vista después de guardar la transferencia
                return redirect('aprobar_transferencia', transferencia.id)
            else:
                # Manejar el caso en que no hay saldo suficiente en la cuenta de origen
                form.add_error(None, 'Saldo insuficiente en la cuenta de origen.')
    else:
        form = TransferenciaForm()
        form.fields['cuenta_origen'].queryset = NuevoRegistro.objects.all()
        form.fields['cuenta_destino'].queryset = NuevoRegistro.objects.all()

    return render(request, 'transferencia_form.html', {'form': form})

def aprobar_transferencia(request, transferencia_id):
    transferencia = get_object_or_404(Transferencia, pk=transferencia_id)
     

    # Lógica para aprobar la transferencia
    if not transferencia.aprobada:
        # Actualizar saldos de cuentas
        cuenta_origen = transferencia.cuenta_origen
        cuenta_destino = transferencia.cuenta_destino

        cuenta_origen.SaldoContable = F('SaldoContable') - transferencia.monto
        cuenta_destino.SaldoContable = F('SaldoContable') + transferencia.monto

        transferencia.aprobada = True

        cuenta_origen.save()
        cuenta_destino.save()
        transferencia.save()

    return render(request, 'aprobar_transferencia.html', {'transferencia': transferencia})

# En detalles_transferencia, puedes obtener las cuentas asociadas a la transferencia:

def detalles_transferencia(request, transferencia_id):
    transferencia = get_object_or_404(Transferencia, pk=transferencia_id)

    # Recupera los detalles de la sesión
    detalles_transferencia = request.session.pop('detalles_transferencia', None)

    if detalles_transferencia:
        # Agrega los detalles a la transferencia
        transferencia.monto = detalles_transferencia['monto']
        transferencia.descripcion = detalles_transferencia['descripcion']
        # Ajusta según sea necesario para otros detalles

    cuenta_origen = transferencia.cuenta_origen
    cuenta_destino = transferencia.cuenta_destino

    return render(request, 'detalles_transferencia.html', {'transferencia': transferencia, 'cuenta_origen': cuenta_origen, 'cuenta_destino': cuenta_destino})

