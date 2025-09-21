from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Usuario, Rol
from .serializers import UsuarioSerializer, RolSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Asignar rol si viene en la request
        rol_id = request.data.get('rol_id')
        if rol_id:
            try:
                rol = Rol.objects.get(id=rol_id)
                user.rol = rol
                user.save()
            except Rol.DoesNotExist:
                return Response({"error": "Rol no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'user': UsuarioSerializer(user).data,  # <-- vuelve a serializar el objeto creado
                'message': 'Usuario registrado exitosamente'
            },
            status=status.HTTP_201_CREATED
        )


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]

    # Listar roles (aunque list() ya lo hace)
    @action(detail=False, methods=['get'], url_path='list-roles')
    def list_roles(self, request):
        roles = self.get_queryset()
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)

    # NOTA: No hace falta definir crear_rol ni editar_rol,
    # porque ModelViewSet ya provee create(), update() y partial_update().

