from rest_framework import viewsets, permissions
from .models import CustomUser
from .api_serializers import UserSerializer, UserCreateSerializer
from .api_permissions import IsAdminOrIsSelf
from rest_framework_simplejwt.views import TokenObtainPairView

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
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

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for the token endpoint to apply a specific throttle scope.
    """
    throttle_scope = 'login'