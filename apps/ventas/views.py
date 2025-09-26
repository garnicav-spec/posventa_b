from rest_framework import viewsets, status
from .models import Venta, DetalleVenta, MetodoPago, FacturaSimulada, VentaPago
from .serializers import (VentaPagoSerializer, VentaSerializer, DetalleVentaSerializer, 
    MetodoPagoSerializer, FacturaSimuladaSerializer, 
    MetodoPagoSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated]
    
    # AGREGAR: Asegurar que el contexto se pasa al serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
           'request': self.request,
        })
        return context

    def perform_create(self, serializer):
        # OPCIONAL: También puedes hacerlo aquí si prefieres
        # serializer.save(usuario=self.request.user)
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def agregar_detalle(self, request, pk=None):
        venta = self.get_object()
        serializer = DetalleVentaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(venta=venta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacturaSimuladaViewSet(viewsets.ModelViewSet):
    queryset = FacturaSimulada.objects.all()
    serializer_class = FacturaSimuladaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generar(self, request):
        """Generar factura simulada"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        factura = serializer.save()
        return Response({
            "mensaje": "Factura simulada generada con éxito",
            "factura": serializer.data
        })


class MetodoPagoViewSet(viewsets.ModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer
    permission_classes = [IsAuthenticated]

class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [IsAuthenticated]

class VentaPagoViewSet(viewsets.ModelViewSet):
    queryset = VentaPago.objects.all()
    serializer_class = VentaPagoSerializer   # ⚠️ esto deberías cambiarlo
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def registrar_pago(self, request):
        """Registrar un pago para una venta"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()
        return Response({
            "mensaje": "Pago registrado con éxito",
            "pago": serializer.data
        })   

