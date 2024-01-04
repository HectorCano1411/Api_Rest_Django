# El código anterior define dos conjuntos de vistas, `NuevoRegistroViewSet` y `TransferenciaViewSet`,
# con varios métodos y permisos para crear y realizar acciones en los objetos `NuevoRegistro` y
# `Transferencia`.
# The above code defines two viewsets, `NuevoRegistroViewSet` and `TransferenciaViewSet`, with various
# methods and permissions for creating and performing actions on `NuevoRegistro` and `Transferencia`
# objects.
from api.permissions import IsAdminUser
from iniciar.models import NuevoRegistro
from transferencias.models import Transferencia
from .serializers import NuevoRegistroSerializer, TransferenciaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.response import Response
from iniciar.models import NuevoRegistro
from transferencias.models import Transferencia
from rest_framework.decorators import action
from django.db import transaction
from .utils import calcular_nuevo_saldo_contable
from django.contrib.auth.hashers import make_password

# La clase `NuevoRegistroViewSet` es un conjunto de vistas que maneja operaciones CRUD para el modelo
# `NuevoRegistro` e incluye una acción personalizada para realizar una transferencia y actualizar el
# saldo.

class NuevoRegistroViewSet(viewsets.ModelViewSet):
    queryset = NuevoRegistro.objects.all()
    serializer_class = NuevoRegistroSerializer

    def perform_create(self, serializer):
        # Antes de guardar el nuevo registro, cifra la contraseña
        raw_password = serializer.validated_data['Clave']
        serializer.validated_data['Clave'] = make_password(raw_password)

        # Guarda el nuevo registro
        serializer.save()
    @action(detail=True, methods=['post'])
    def realizar_transferencia(self, request, pk=None):
        nuevo_registro = self.get_object()
        serializer = TransferenciaSerializer(data=request.data)

        if serializer.is_valid():
            with transaction.atomic():
                # Obtener el objeto Transferencia recién creada
                transferencia = serializer.save(nuevo_registro=nuevo_registro)
                
                # Actualizar el saldo en el NuevoRegistro
                nuevo_registro.saldo_contable = calcular_nuevo_saldo_contable(transferencia)
                nuevo_registro.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# El código anterior define dos conjuntos de vistas para los modelos NuevoRegistro y Transferencia,
# con serializadores y clases de permisos específicos.
class NuevoRegistroViewSet(viewsets.ModelViewSet):
    queryset = NuevoRegistro.objects.all()
    serializer_class = NuevoRegistroSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
# La clase TransferenciaViewSet es un conjunto de vistas que maneja operaciones CRUD para objetos
# Transferencia, utiliza TransferenciaSerializer para la serialización y requiere autenticación y
# permisos de usuario administrador.
class TransferenciaViewSet(viewsets.ModelViewSet):
    queryset = Transferencia.objects.all()
    serializer_class = TransferenciaSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

