from rest_framework import viewsets, permissions
from .models import CustomUser
from .api_serializers import UserSerializer, UserCreateSerializer
from .api_permissions import IsAdminOrIsSelf
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Usuários'])
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.

    **Permissions:**
    - **Admins:** Full access (list, create, view, edit, delete all users).
    - **Authenticated Users:** Can only view and edit their own profile. Cannot list or create other users.
    """

    queryset = CustomUser.objects.all().order_by('-date_joined')
    permission_classes = [IsAdminOrIsSelf]

    filterset_fields = ['user_type', 'is_active']

    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the request action.
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @extend_schema(
        summary="Listar Usuários (Apenas Admins)",
        description="Retorna uma lista de todos os usuários do sistema. Acesso restrito a administradores."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar um Novo Usuário (Apenas Admins)")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Consultar um Usuário Específico")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Usuário (Completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Usuário (Parcial)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Excluir um Usuário (Apenas Admins)")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

@extend_schema(tags=['Autenticação'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for the token endpoint to apply a specific throttle scope.
    """
    throttle_scope = 'login'

@extend_schema(tags=['Autenticação']) # 4. Adicione o decorador aqui também
class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for the token refresh endpoint.
    """
    pass