# api/serializers.py
from rest_framework import serializers
from iniciar.models import NuevoRegistro
from transferencias.models import Transferencia

class NuevoRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = NuevoRegistro
        fields = '__all__'

class TransferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transferencia
        fields = '__all__'
