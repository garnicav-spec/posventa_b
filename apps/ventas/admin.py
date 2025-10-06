from django.contrib import admin
from .models import Venta, DetalleVenta, FacturaSimulada, MetodoPago, VentaPago

# Inlines
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    fields = ['producto', 'cantidad', 'precio_unitario', 'descuento', 'subtotal']
    readonly_fields = ['subtotal']

class VentaPagoInline(admin.TabularInline):
    model = VentaPago
    extra = 0
    fields = ['metodo_pago', 'monto', 'referencia']

# Admin para Venta
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_hora', 'sucursal', 'usuario', 'cliente', 'estado_venta', 'total_bruto', 'total_descuento', 'total_neto')
    list_filter = ('sucursal', 'estado_venta', 'fecha_hora')
    search_fields = ('id', 'cliente__nombre', 'usuario__username')
    date_hierarchy = 'fecha_hora'
    inlines = [DetalleVentaInline, VentaPagoInline]

    # Excluir 'fecha_hora' del form
    fieldsets = (
        ("Información de la Venta", {
            "fields": ('sucursal', 'usuario', 'cliente', 'estado_venta')  # Excluyendo 'fecha_hora'
        }),
        ("Totales", {
            "fields": ('total_bruto', 'total_descuento', 'total_neto')
        }),
    )

admin.site.register(Venta, VentaAdmin)

# Admin para DetalleVenta
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'precio_unitario', 'descuento', 'subtotal', 'venta')
    search_fields = ('producto__nombre', 'venta__id')
    list_filter = ('venta',)

admin.site.register(DetalleVenta, DetalleVentaAdmin)



# Admin para FacturaSimulada
class FacturaSimuladaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'venta', 'fecha_emision', 'nit_ci', 'razon_social', 'nombre_cliente')
    search_fields = ('numero_factura', 'venta__id', 'nit_ci', 'nombre_cliente')
    list_filter = ('fecha_emision',)

admin.site.register(FacturaSimulada, FacturaSimuladaAdmin)

# Admin para MetodoPago
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(MetodoPago, MetodoPagoAdmin)

# Admin para VentaPago
class VentaPagoAdmin(admin.ModelAdmin):
    list_display = ('venta', 'metodo_pago', 'monto', 'referencia')
    search_fields = ('venta__id', 'metodo_pago__nombre', 'referencia')
    list_filter = ('metodo_pago',)

admin.site.register(VentaPago, VentaPagoAdmin)
