from rest_framework import serializers
from .models import LogAuditoria, ArqueoCaja


class LogAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogAuditoria
        fields = "__all__"

class ArqueoCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArqueoCaja
        fields = "__all__"