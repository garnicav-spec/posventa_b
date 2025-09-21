from rest_framework import serializers
from .models import (
    Producto, ImagenProducto, 
    InventarioSucursal, MovimientoInventario, 
    MovimientoInventarioDetalle, 
)

class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = "__all__"

class ProductoSerializer(serializers.ModelSerializer):
    imagenes = ImagenProductoSerializer(many=True, source="imagenproducto_set", read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "codigo_barras",
            "codigo",
            "nombre",
            "unidad",
            "precio_venta",
            "costo_promedio",
            "activo",
            "imagenes",
        ]

class InventarioSucursalSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)

    class Meta:
        model = InventarioSucursal
        fields = [
            "id",
            "sucursal",
            "producto",
            "stock_actual",
            "stock_minimo",
        ]

class MovimientoInventarioDetalleSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)

    class Meta:
        model = MovimientoInventarioDetalle
        fields = [
            "id",
            "movimiento",
            "producto",
            "cantidad",
            "costo_unitario",
        ]

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    detalles = MovimientoInventarioDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = [
            "id",
            "sucursal",
            "usuario",
            "fecha_hora",
            "tipo_movimiento",
            "origen_tipo",
            "origen_id",
            "observacion",
            "detalles",
        ]


