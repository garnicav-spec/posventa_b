from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # Para la autenticación de DRF
    
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("api.urls")),
    
    path('inventario/', include('apps.inventario.urls')),
    path('negocio/', include('apps.negocio.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('user/', include('apps.usuarios.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('', TemplateView.as_view(template_name='index.html')),  # Para servir React
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
