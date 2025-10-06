from django.db import transaction
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Max

from .models import Venta, DetalleVenta, MetodoPago, FacturaSimulada, VentaPago
from .serializers import (
    VentaSerializer,
    DetalleVentaSerializer,
    MetodoPagoSerializer,
    FacturaSimuladaSerializer,
    VentaPagoSerializer,
)

from apps.inventario.models import (
    InventarioSucursal,
    MovimientoInventario,
    MovimientoInventarioDetalle,
)

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated]

    # El serializer necesita el request para CurrentUserDefault, etc.
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx.update({"request": self.request})
        return ctx

    # Redundante con HiddenField, pero explícito no hace daño
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=["post"])
    def agregar_detalle(self, request, pk=None):
        venta = self.get_object()
        ser = DetalleVentaSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        if ser.is_valid():
            ser.save(venta=venta)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        venta_antes = Venta.objects.get(pk=self.get_object().pk)
        estado_antes = venta_antes.estado_venta_id

        with transaction.atomic():
            venta = serializer.save()
            estado_despues = venta.estado_venta_id

            # IDs definidos en admin
            EN_PROCESO = 1
            PAGADA = 2
            ANULADA = 3

            # ----- PAGADA: consumir reserva (NO tocar stock; solo movimiento SALIDA) -----
            if estado_antes != PAGADA and estado_despues == PAGADA:
                # Evitar duplicar movimientos si alguien vuelve a En Proceso y otra vez a Pagada
                existe_salida = MovimientoInventario.objects.filter(
                    sucursal=venta.sucursal,
                    origen_tipo="VENTA",
                    origen_id=venta.id,
                    tipo_movimiento="Salida",
                ).exists()
                if not existe_salida:
                    mov = MovimientoInventario.objects.create(
                        sucursal=venta.sucursal,
                        usuario=self.request.user,
                        tipo_movimiento="Salida",  # respeta tus choices/literales
                        origen_tipo="VENTA",
                        origen_id=venta.id,
                        observacion=f"Venta {venta.id} pagada (consumo de reserva)",
                    )
                    for det in venta.detalles.all():
                        MovimientoInventarioDetalle.objects.create(
                            movimiento=mov,
                            producto=det.producto,
                            cantidad=det.cantidad,
                            # ajusta si usas costo_promedio u otro campo
                            costo_unitario=det.precio_unitario,
                        )

            # ----- ANULADA: devolver reserva (sumar stock). Si venía de Pagada => ENTRADA -----
            elif estado_antes in (EN_PROCESO, PAGADA) and estado_despues == ANULADA:
                # 1) Reponer stock reservado
                for det in venta.detalles.select_for_update():
                    inv, _ = (
                        InventarioSucursal.objects.select_for_update().get_or_create(
                            sucursal=venta.sucursal,
                            producto=det.producto,
                            defaults={"stock_actual": 0, "stock_minimo": 0},
                        )
                    )
                    inv.stock_actual += det.cantidad
                    inv.save()

                # 2) Si ya estaba pagada, documentar ENTRADA por anulación.
                if estado_antes == PAGADA:
                    existe_entrada = MovimientoInventario.objects.filter(
                        sucursal=venta.sucursal,
                        origen_tipo="ANULACION_VENTA",
                        origen_id=venta.id,
                        tipo_movimiento="Entrada",
                    ).exists()
                    if not existe_entrada:
                        mov = MovimientoInventario.objects.create(
                            sucursal=venta.sucursal,
                            usuario=self.request.user,
                            tipo_movimiento="Entrada",
                            origen_tipo="ANULACION_VENTA",
                            origen_id=venta.id,
                            observacion=f"Anulación de venta {venta.id} (devolución de reserva)",
                        )
                        for det in venta.detalles.all():
                            MovimientoInventarioDetalle.objects.create(
                                movimiento=mov,
                                producto=det.producto,
                                cantidad=det.cantidad,
                                costo_unitario=det.precio_unitario,
                            )

            # Después de procesar la venta, generamos automáticamente la factura
            self.generar_factura(venta)

    def generar_factura(self, venta):
        """Genera la factura automáticamente cuando la venta se procesa"""
        try:
            # Generar los datos de la factura
            numero_factura = FacturaSimulada.generar_numero_factura()

            # Recoger los detalles de la venta
            detalles_venta = [
                {
                    'producto': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'precio_unitario': detalle.precio_unitario,
                    'descuento': detalle.descuento,
                    'subtotal': detalle.subtotal
                }
                for detalle in venta.detalles.all()
            ]
            
            # Crear la factura simulada
            factura_data = {
                'venta': venta,
                'numero_factura': numero_factura,
                'fecha_emision': timezone.now(),
                'nit_ci': venta.cliente.nit if venta.cliente else '',
                'razon_social': venta.cliente.razon_social if venta.cliente else '',
                'nombre_cliente': venta.cliente.nombre if venta.cliente else '',
                'detalles_venta': detalles_venta
            }

            # Usamos el serializador para crear la factura
            factura_serializer = FacturaSimuladaSerializer(data=factura_data)
            factura_serializer.is_valid(raise_exception=True)
            factura_serializer.save()

            return Response({
                "mensaje": "Factura generada exitosamente",
                "factura": factura_serializer.data
            })

        except Exception as e:
            return Response({"mensaje": f"Error generando factura: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)                            

class FacturaSimuladaViewSet(viewsets.ModelViewSet):
    queryset = FacturaSimulada.objects.all()
    serializer_class = FacturaSimuladaSerializer

    @action(detail=True, methods=["post"])
    def generar(self, request, pk=None):
        print("Solicitud de generar factura recibida")
        try:
            venta = Venta.objects.get(pk=pk)
            print("Venta encontrada:", venta)

            # Obtener datos del cliente y detalles de la venta
            cliente = venta.cliente
            nit_ci = cliente.nit if cliente else ""
            razon_social = cliente.razon_social if cliente else ""
            nombre_cliente = cliente.nombre if cliente else "Cliente General"

            detalles_venta = [
                {
                    'producto': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'precio_unitario': detalle.precio_unitario,
                    'descuento': detalle.descuento,
                    'subtotal': detalle.subtotal
                }
                for detalle in venta.detalles.all()
            ]

            # Crear factura simulada
            factura = FacturaSimulada.objects.create(
                venta=venta,
                numero_factura=FacturaSimulada.generar_numero_factura(),
                fecha_emision=timezone.now(),
                nit_ci=nit_ci,
                razon_social=razon_social,
                nombre_cliente=nombre_cliente,
                detalles_venta=detalles_venta
            )

            serializer = FacturaSimuladaSerializer(factura)
            print("Factura generada:", serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Venta.DoesNotExist:
            return Response({"error": "Venta no encontrada."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def generar_numero_factura(self):
        """Generar el número de factura incrementando con cada venta."""
        ultimo_factura = FacturaSimulada.objects.aggregate(Max('numero_factura'))
        ultimo_numero = ultimo_factura['numero_factura__max']
        
        if ultimo_numero:
            nuevo_numero = int(ultimo_numero.split('-')[1]) + 1
        else:
            nuevo_numero = 1

        return f"FAC-{nuevo_numero:05d}"  # Formato de factura FAC-00001

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


