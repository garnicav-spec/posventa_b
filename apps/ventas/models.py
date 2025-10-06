from django.db import models
from django.utils import timezone
from django.db.models import Max
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from apps.negocio.models import Sucursal, Cliente, EstadoVenta
from apps.usuarios.models import Usuario
from apps.inventario.models import Producto


class Venta(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="venta")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    estado_venta = models.ForeignKey(EstadoVenta, on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    total_bruto = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_descuento = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        app_label = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        db_table = 'venta'

    def __str__(self):
        return f"Venta {self.id} - {self.fecha_hora}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2)
    descuento = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = (self.cantidad * self.precio_unitario) - self.descuento
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'ventas'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
        db_table = 'detalle_venta'

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


class FacturaSimulada(models.Model):
    venta = models.ForeignKey('ventas.Venta', on_delete=models.CASCADE)
    numero_factura = models.CharField(max_length=100, unique=True)
    fecha_emision = models.DateTimeField(default=timezone.now)
    nit_ci = models.CharField(max_length=30, blank=True, null=True)
    razon_social = models.CharField(max_length=255, blank=True, null=True)
    nombre_cliente = models.CharField(max_length=255, blank=True, null=True)
    detalles_venta = models.JSONField()  # Para almacenar los detalles de la venta en formato JSON
    
    class Meta:
        app_label = 'ventas'
        verbose_name = 'Factura Simulada'
        verbose_name_plural = 'Facturas Simuladas'
        db_table = 'factura_simulada'

    def __str__(self):
        return f"Factura {self.numero_factura} - Venta {self.venta.id}"

    @staticmethod
    def generar_numero_factura():
        """Generar el número de factura incrementando con cada venta."""
        ultimo_factura = FacturaSimulada.objects.aggregate(Max('numero_factura'))
        ultimo_numero = ultimo_factura['numero_factura__max']
        
        if ultimo_numero:
            nuevo_numero = int(ultimo_numero.split('-')[1]) + 1
        else:
            nuevo_numero = 1

        return f"FAC-{nuevo_numero:05d}"

    def save(self, *args, **kwargs):
        if not self.numero_factura:
            self.numero_factura = FacturaSimulada.generar_numero_factura()
        
        if self.venta:
            self.nit_ci = self.venta.cliente.nit if self.venta.cliente else ""
            self.razon_social = self.venta.cliente.razon_social if self.venta.cliente else ""
            self.nombre_cliente = self.venta.cliente.nombre if self.venta.cliente else ""
            self.detalles_venta = [
                {
                    'producto': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'precio_unitario': detalle.precio_unitario,
                    'descuento': detalle.descuento,
                    'subtotal': detalle.subtotal
                }
                for detalle in self.venta.detalles.all()
            ]
        
        super().save(*args, **kwargs)

class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
            app_label = 'ventas'
            verbose_name = 'Metodo Pago'
            verbose_name_plural = 'Metodos de Pago'
            db_table = 'metodo_pago'    

    def __str__(self):
        return f"Factura {self.nombre}"
    
class VentaPago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    referencia = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'ventas'
        verbose_name = 'Pago de Venta'
        verbose_name_plural = 'Pagos de Ventas'
        db_table = 'venta_pago'

    def __str__(self):
        return f"Pago de {self.monto} - {self.metodo_pago.nombre}"

