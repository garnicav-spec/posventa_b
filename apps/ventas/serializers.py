from rest_framework import serializers
from .models import Venta, DetalleVenta, MetodoPago, FacturaSimulada, VentaPago
from apps.inventario.models import InventarioSucursal

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = DetalleVenta
        fields = ["id", "producto", "producto_nombre", "cantidad", "precio_unitario", "descuento", "subtotal"]
        
class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Venta
        fields = "__all__"

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        # CORRECCIÓN CRÍTICA: Asignar usuario automáticamente
        if 'usuario' not in validated_data:
            validated_data['usuario'] = self.context['request'].user
        
        venta = Venta.objects.create(**validated_data)

        total_bruto = 0
        total_descuento = 0
        
        for detalle in detalles_data:
            producto = detalle['producto']
            cantidad = detalle['cantidad']
            precio_unitario = detalle['precio_unitario']
            descuento = detalle.get('descuento', 0)
            

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                descuento=descuento
                # subtotal se calcula automáticamente en el modelo
            )

            # Actualizar stock
            try:
                inventario = InventarioSucursal.objects.get(
                    sucursal=venta.sucursal,
                    producto=producto
                )
                if inventario.stock_actual < cantidad:
                    raise serializers.ValidationError(f"No hay suficiente stock de {producto.nombre}.")
                inventario.stock_actual -= cantidad
                inventario.save()
            except InventarioSucursal.DoesNotExist:
                raise serializers.ValidationError(f"El producto {producto.nombre} no tiene stock en esta sucursal.")

            total_bruto += (cantidad * precio_unitario)
            total_descuento += descuento

        # CORREGIR: usar los nombres correctos de campo del modelo
        venta.total_bruto = total_bruto
        venta.total_descuento = total_descuento
        venta.total_neto = total_bruto - total_descuento
        venta.save()

        return venta

class FacturaSimuladaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaSimulada
        fields = ["id", "nit_ci", "razon_social", "numero_factura", "fecha_emision"]

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = "__all__"

class VentaPagoSerializer(serializers.ModelSerializer):
    metodo_pago = MetodoPagoSerializer(read_only=True)
    metodo_pago_id = serializers.PrimaryKeyRelatedField(
        queryset=MetodoPago.objects.all(), source="metodo_pago", write_only=True
    )

    class Meta:
        model = VentaPago
        fields = ["id", "metodo_pago", "metodo_pago_id", "monto", "referencia"]

    