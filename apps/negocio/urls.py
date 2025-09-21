from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClienteViewSet, SucursalViewSet, PuntoVentaViewSet
    , EstadoVentaViewSet, CiudadViewSet,
    ClienteListView
)

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'sucursales', SucursalViewSet)
router.register(r'puntos-venta', PuntoVentaViewSet)
router.register(r'estados-venta', EstadoVentaViewSet)
router.register(r'ciudades', CiudadViewSet)
router.register(r'cliente-list', ClienteListView, basename='cliente-list')

urlpatterns = [
    path('', include(router.urls)),
]