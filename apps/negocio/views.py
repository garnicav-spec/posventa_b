from rest_framework import viewsets
from .models import (
    Cliente, Sucursal, PuntoVenta
    , EstadoVenta, Ciudad
)
from .serializers import (
    ClienteSerializer, SucursalSerializer
    , PuntoVentaSerializer, EstadoVentaSerializer,
    CiudadSerializer
)
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    
class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [IsAuthenticated]

class PuntoVentaViewSet(viewsets.ModelViewSet):
    queryset = PuntoVenta.objects.all()
    serializer_class = PuntoVentaSerializer
    permission_classes = [IsAuthenticated]

class ClienteListView(viewsets.ViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return render(request, 'negocio/cliente_list.html', {'clientes': serializer.data})
    
class EstadoVentaViewSet(viewsets.ModelViewSet):
    queryset = EstadoVenta.objects.all()
    serializer_class = EstadoVentaSerializer
    permission_classes = [IsAuthenticated]

class CiudadViewSet(viewsets.ModelViewSet):
    queryset = Ciudad.objects.all()
    serializer_class = CiudadSerializer
    permission_classes = [IsAuthenticated]
