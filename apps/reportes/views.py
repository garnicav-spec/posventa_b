from rest_framework import viewsets
from .models import LogAuditoria, ArqueoCaja
from .serializers import LogAuditoriaSerializer, ArqueoCajaSerializer
from rest_framework.permissions import IsAuthenticated

class LogAuditoriaViewSet(viewsets.ModelViewSet):
    queryset = LogAuditoria.objects.all()
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAuthenticated]

class ArqueoCajaViewSet(viewsets.ModelViewSet):
    queryset = ArqueoCaja.objects.all()
    serializer_class = ArqueoCajaSerializer
    permission_classes = [IsAuthenticated]

    
