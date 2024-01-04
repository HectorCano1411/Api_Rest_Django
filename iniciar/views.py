import re
from decimal import Decimal
from django.urls import reverse
from transferencias.models import Transferencia
from .models import NuevoRegistro
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password ,check_password
from django.shortcuts import render, redirect
from django.contrib import messages 
from django.db import IntegrityError
from .forms import AdminAuthenticationForm, RegistroNuevoForm
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import authenticate, login
from .forms import AdminAuthenticationForm
from .models import NuevoRegistro
from datetime import timedelta
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from datetime import datetime

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroNuevoForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            clave = form.cleaned_data['clave1']
            usuario.Clave = make_password(clave)

            # Añade la validación para establecer el TipoCuenta por defecto a CUENTA_CORRIENTE
            if not usuario.TipoCuenta:
                usuario.TipoCuenta = NuevoRegistro.CUENTA_CORRIENTE

            try:
                usuario.save()
                print('Clave guardada exitosamente en la base de datos')
                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
                return redirect('custom_login')
            except Exception as e:
                print(f'Error al guardar la clave en la base de datos: {e}')
                messages.error(request, 'Hubo un error al guardar la clave. Por favor, inténtalo de nuevo.')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistroNuevoForm()
    return render(request, 'registro_usuario.html', {'form': form})


# def custom_login(request):
#     if request.method == 'POST':
#         rut = request.POST.get('rut')
#         clave = request.POST.get('clave')
#         try:
#             usuario = NuevoRegistro.objects.get(rut=rut)
#             if not usuario.Estado:
#                 messages.warning(request, 'Tu cuenta está bloqueada. Contacta al soporte.')
#                 return render(request, 'login.html')
#             if check_password(clave, usuario.Clave):
#                 usuario.intentos_fallidos = 0  # Reiniciar intentos fallidos
#                 usuario.save()

#                 # Almacena el RUT del usuario autenticado en la sesión
#                 request.session['rut'] = rut
#                 request.session.set_expiry(timezone.now() + timedelta(seconds=120))


#                 return redirect('detalle_cuenta', usuario_id=usuario.id)
#             usuario.intentos_fallidos += 1
#             if usuario.intentos_fallidos == 1:
#                 messages.warning(request, 'Primer intento fallido.')
#             elif usuario.intentos_fallidos == 2:
#                 messages.warning(request, 'Segundo intento fallido. Le queda un intento.')
#             elif usuario.intentos_fallidos >= 3:
#                 usuario.Estado = False
#                 usuario.save()
#                 messages.error(request, 'Tu cuenta ha sido bloqueada. Por favor, contacta al soporte.')

#             usuario.save()  # Guardar cambios en los intentos fallidos
#         except NuevoRegistro.DoesNotExist:
#             messages.error(request, 'Usuario no encontrado')

#     return render(request, 'login.html')

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect


# Resto del código de la vista custom_login
def custom_login(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        clave = request.POST.get('clave')
        try:
            usuario = NuevoRegistro.objects.get(rut=rut)
            if not usuario.Estado:
                messages.warning(request, 'Tu cuenta está bloqueada. Contacta al soporte.')
                return render(request, 'login.html')
            if check_password(clave, usuario.Clave):
                usuario.intentos_fallidos = 0  # Reiniciar intentos fallidos
                usuario.save()

                # Serializa manualmente la fecha de expiración
                expiracion = (timezone.now() + timedelta(seconds=180)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                # Almacena el RUT del usuario autenticado y la fecha de expiración en la sesión
                request.session['rut'] = rut
                request.session['expiracion'] = expiracion

                return redirect('detalle_cuenta', usuario_id=usuario.id)
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos == 1:
                messages.warning(request, 'Primer intento fallido.')
            elif usuario.intentos_fallidos == 2:
                messages.warning(request, 'Segundo intento fallido. Le queda un intento.')
            elif usuario.intentos_fallidos >= 3:
                usuario.Estado = False
                usuario.save()
                messages.error(request, 'Tu cuenta ha sido bloqueada. Por favor, contacta al soporte.')

            usuario.save()  # Guardar cambios en los intentos fallidos
        except NuevoRegistro.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')

    return render(request, 'login.html')



def custom_logout(request):
    # Verifica si se debe mostrar la alerta
    show_warning = request.GET.get('show_warning', False)

    # Realiza acciones de cierre de sesión si es necesario
    request.session.flush()

    # Renderiza la plantilla con la alerta si es necesario
    if show_warning:
        return render(request, 'logout_with_warning.html', {'show_warning': True})
    else:
        return redirect('custom_login')
   

def ingresar_valor(request, usuario_id):
    try:
        usuario = NuevoRegistro.objects.get(id=usuario_id)

        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            rut_ingresado = request.POST.get('rut')
            monto_str = request.POST.get('monto', '0')

            # Verificar que el RUT almacenado en la sesión coincida con el RUT ingresado
            rut_autenticado = request.session.get('rut')
            if rut_autenticado != rut_ingresado:
                messages.error(request, 'El RUT ingresado no coincide con tu RUT del Titular.')
                return render(request, 'ingresar_valor.html', {'usuario': usuario})

            # Validar que el monto sea un valor entero
            if not monto_str.isdigit():
                messages.error(request, 'Solo se pueden ingresar valores enteros mayores a 0.')
                return render(request, 'ingresar_valor.html', {'usuario': usuario})

            monto = Decimal(monto_str)

            if monto <= Decimal('0'):
                messages.error(request, 'El monto debe ser mayor que cero.')
            else:
                # Validar que el TipoCuenta sea 'Cuenta Corriente'
                if usuario.TipoCuenta != NuevoRegistro.CUENTA_CORRIENTE:
                    messages.error(request, 'Solo se pueden ingresar valores a cuentas corrientes.')
                    return render(request, 'ingresar_valor.html', {'usuario': usuario})

                # Resto del código para ingresar el valor
                if usuario.SaldoCuentaCorriente is None:
                    usuario.SaldoCuentaCorriente = Decimal('0.0')

                # Realizar la operación de ingreso de valor y actualizar el saldo
                if usuario.SaldoCuentaCorriente is not None:
                    usuario.SaldoCuentaCorriente += monto
                else:
                    usuario.SaldoCuentaCorriente = monto

                usuario.save()
                messages.success(request, f'Se ingresó ${monto} a la cuenta de {nombre} (RUT: {rut_ingresado}) exitosamente.')

                # Actualizar SaldoContable y SaldoLineaCredito en la vista detalle_cuenta
                if usuario.SaldoCuentaCorriente is not None:
                    usuario.SaldoContable = usuario.SaldoCuentaCorriente
                    usuario.SaldoLineaCredito = usuario.SaldoCuentaCorriente * Decimal('0.8')  # Ejemplo de cálculo
                    usuario.save()
                    
                if usuario.TotalAbonos is not None:
                    usuario.TotalAbonos += monto
                else:
                    usuario.TotalAbonos = monto

                usuario.save()

                # Aquí convierte el objeto Decimal a un número de punto flotante
                monto_float = float(monto)

                # Guarda los datos necesarios en la sesión para la vista de comprobante
                request.session['nombre'] = nombre
                request.session['rut'] = rut_ingresado
                request.session['monto'] = monto_float

                # Redirecciona a la vista 'comprobante'
                return redirect('comprobante', usuario_id=usuario_id)

    except NuevoRegistro.DoesNotExist:
        messages.error(request, 'El usuario no existe.')

    return render(request, 'ingresar_valor.html', {'usuario': usuario})


def realizar_retiro(request, usuario_id):
    try:
        usuario = NuevoRegistro.objects.get(id=usuario_id)
    except NuevoRegistro.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('detalle_cuenta', usuario_id=usuario_id)

    if request.method == 'POST':
        monto = request.POST.get('monto', '0.0')  # Obtener el monto como cadena

        if not monto.isdigit():
            messages.error(request, 'Solo se pueden retirar valores enteros y el monto debe ser mayor a 0.')
            return redirect('realizar_retiro', usuario_id=usuario_id)

        monto_decimal = Decimal(monto)  # Convertir la cadena a Decimal

        if monto_decimal <= Decimal('0.0'):
            messages.error(request, 'El monto a retirar debe ser mayor que cero.')
        elif monto_decimal > usuario.SaldoCuentaCorriente:
            messages.error(request, 'No tienes suficientes fondos para realizar este retiro.')
        else:
            with transaction.atomic():
                # Realizar la operación de retiro de valor y actualizar el saldo
                usuario.SaldoCuentaCorriente -= monto_decimal

                # Actualizar TotalCargos con el monto del retiro
                if usuario.TotalCargos is not None:
                    usuario.TotalCargos -= monto_decimal
                else:
                    usuario.TotalCargos = monto_decimal

                usuario.save()
                messages.success(request, f'Se retiró ${monto_decimal} de la cuenta exitosamente.')

                # Datos a enviar a la vista de comprobante
                nombre = usuario.Nombres
                rut = usuario.rut

                # Guarda los datos necesarios en la sesión para la vista de comprobante
                request.session['nombre'] = nombre
                request.session['rut'] = rut
                request.session['monto'] = float(monto_decimal)  # Convierte el Decimal a float

                return redirect('comprobante_retiro', usuario_id=usuario_id)

    return render(request, 'realizar_retiro.html', {'usuario': usuario})


def comprobante(request, usuario_id):
    try:
        usuario = NuevoRegistro.objects.get(id=usuario_id)
        # Obtiene los datos de la transacción del último mensaje en la sesión
        nombre = request.session.get('nombre')
        rut = request.session.get('rut')
        monto = request.session.get('monto')
        fecha_y_hora = request.session.get('fecha_y_hora')

        # Ajusta los campos según tu modelo
        # Por ejemplo, puedes agregar otros campos como 'NumeroCuenta', 'SaldoCuentaCorriente', etc.
        detalle_cuenta_url = reverse('detalle_cuenta', args=[usuario_id])
        
        


        return render(request, 'comprobante.html', {
            'detalle_cuenta_url': detalle_cuenta_url,
            'usuario': usuario,
            'nombre': nombre,
            'rut': rut,
            'monto': monto,
            'fecha_y_hora': fecha_y_hora, 
        })

    except NuevoRegistro.DoesNotExist:
        raise Http404("Usuario no encontrado")


def comprobante_retiro(request, usuario_id):
    usuario = get_object_or_404(NuevoRegistro, id=usuario_id)

    nombre = request.session.get('nombre')
    rut = request.session.get('rut')
    monto = request.session.get('monto')
    detalle_cuenta_url = reverse('detalle_cuenta', args=[usuario_id])


    return render(request, 'comprobante_retiro.html', {
        'detalle_cuenta_url': detalle_cuenta_url,
        'usuario': usuario,
        'nombre': nombre,
        'rut': rut,
        'monto': monto,
    })



# def detalle_cuenta(request, usuario_id): FUE MODIFICADA ESTA VISTA PARA PODER SERIALIZAR LOS DATE TIME
#     try:
#         usuario = NuevoRegistro.objects.get(id=usuario_id)        
#         numero_cuenta = usuario.NumeroCuenta  # Obtener el valor de NumeroCuenta
#         now = datetime.now()
#         context = {
#             'usuario': usuario,
#             'numero_cuenta': numero_cuenta,  # Agregar numero_cuenta al contexto
#             'fecha_actual': now,
#         }
#         return render(request, 'detalle_cuenta.html', context)
#     except NuevoRegistro.DoesNotExist:
#         messages.error(request, 'Usuario no encontrado')
    
#     return redirect('custom_login')
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

# Resto del código de la vista detalle_cuenta FUE MODIFICADA ESTA VISTA PARA PODER SERIALIZAR INCORPORAR  Y MOSTRAR LAS TRANSACCIONES
# def detalle_cuenta(request, usuario_id):
#     try:
#         usuario = NuevoRegistro.objects.get(id=usuario_id)        
#         numero_cuenta = usuario.NumeroCuenta  # Obtener el valor de NumeroCuenta
#         now = datetime.now()

#         # Serializar manualmente el objeto datetime
#         serialized_now = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

#         # Agregar el objeto serializado al contexto
#         context = {
#             'usuario': usuario,
#             'numero_cuenta': numero_cuenta,
#             'fecha_actual': serialized_now,
#         }

#         return render(request, 'detalle_cuenta.html', context)
#     except NuevoRegistro.DoesNotExist:
#         messages.error(request, 'Usuario no encontrado')
    
#     return redirect('custom_login')

# from django.shortcuts import get_object_or_404
# from django.db.models import Q

# def detalle_cuenta(request, usuario_id):
#     try:
#         usuario = get_object_or_404(NuevoRegistro, id=usuario_id)

#         # Obtener transacciones asociadas con el usuario
#         transacciones = Transferencia.objects.filter(Q(cuenta_origen=usuario) | Q(cuenta_destino=usuario))

#         numero_cuenta = usuario.NumeroCuenta
#         now = datetime.now()
#         serialized_now = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

#         context = {
#             'usuario': usuario,
#             'numero_cuenta': numero_cuenta,
#             'fecha_actual': serialized_now,
#             'transacciones': transacciones,
#         }

#         return render(request, 'detalle_cuenta.html', context)
#     except NuevoRegistro.DoesNotExist:
#         messages.error(request, 'Usuario no encontrado')

#     return redirect('custom_login')
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import NuevoRegistro
from transferencias.models import Transferencia
from datetime import datetime
from django.http import JsonResponse

def detalle_cuenta(request, usuario_id):
    try:
        usuario = get_object_or_404(NuevoRegistro, id=usuario_id)
        transacciones = Transferencia.objects.filter(Q(cuenta_origen=usuario) | Q(cuenta_destino=usuario))
        numero_cuenta = usuario.NumeroCuenta
        now = datetime.now()
        serialized_now = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        context = {
            'usuario': usuario,
            'numero_cuenta': numero_cuenta,
            'fecha_actual': serialized_now,
            'transacciones': transacciones,
        }

        return render(request, 'detalle_cuenta.html', context)
    except NuevoRegistro.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')

    return redirect('custom_login')

def actualizar_saldo_contable(request, usuario_id):
    if request.method == 'GET' and request.is_ajax():
        usuario = get_object_or_404(NuevoRegistro, id=usuario_id)
        saldo_contable = usuario.SaldoContable
        return JsonResponse({'saldo_contable': saldo_contable})

    return JsonResponse({}, status=400)
    
def movimientos(request, usuario_id):
    try:
        usuario = get_object_or_404(NuevoRegistro, id=usuario_id)

        # Obtener transacciones asociadas con el usuario
        transacciones = Transferencia.objects.filter(Q(cuenta_origen=usuario) | Q(cuenta_destino=usuario))

        numero_cuenta = usuario.NumeroCuenta
        now = datetime.now()
        serialized_now = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        context = {
            'usuario': usuario,
            'numero_cuenta': numero_cuenta,
            'fecha_actual': serialized_now,
            'transacciones': transacciones,
        }

        return render(request, 'movimientos.html', context)
    except NuevoRegistro.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')

    return redirect('custom_login')


@login_required
def lista_usuarios(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        # El usuario no está autenticado o no es un administrador, redirige a la página de autenticación de administrador
        return redirect('admin_login')

    usuarios = NuevoRegistro.objects.all()
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

def bloquear_usuario(request, usuario_id):
    usuario = get_object_or_404(NuevoRegistro, pk=usuario_id)
    usuario.Estado = not usuario.Estado
    usuario.save()
    return redirect('lista_usuarios')


def admin_login(request):
    if request.method == 'POST':
        form = AdminAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # El administrador ha ingresado con éxito, puedes redirigirlo a la lista de usuarios para bloquear
                login(request, user)
                return redirect('lista_usuarios')  # Reemplaza 'lista_usuarios' con la URL de tu lista de usuarios
    else:
        form = AdminAuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})

