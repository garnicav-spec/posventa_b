from rest_framework import serializers
from .models import Venta, DetalleVenta, MetodoPago, FacturaSimulada, VentaPago
from apps.inventario.models import InventarioSucursal

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = DetalleVenta
        fields = ["id", "producto", "producto_nombre", "cantidad", "precio_unitario", "descuento", "subtotal"]
        
class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)  # 👈 se anidan detalles dentro de una venta

    class Meta:
        model = Venta
        fields = "__all__"

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')  # extraemos los detalles
        venta = Venta.objects.create(**validated_data)

        total = 0
        for detalle in detalles_data:
            producto = detalle['producto']
            cantidad = detalle['cantidad']
            subtotal = cantidad * detalle['precio_unitario']

            # crear el detalle
            DetalleVenta.objects.create(
                venta=venta,
                **detalle,
                sub_total=subtotal
            )

            # actualizar stock
            try:
                inventario = InventarioSucursal.objects.get(
                    sucursal=venta.sucursal,
                    producto=producto
                )
                if inventario.stock_actual < cantidad:
                    raise serializers.ValidationError(f"No hay suficiente stock de {producto}.")
                inventario.stock_actual -= cantidad
                inventario.save()
            except InventarioSucursal.DoesNotExist:
                raise serializers.ValidationError(f"El producto {producto} no tiene stock en esta sucursal.")

            total += subtotal

        # actualizar totales de la venta
        venta.total_venta = total
        venta.total_neto = total - venta.total_descuento
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

    