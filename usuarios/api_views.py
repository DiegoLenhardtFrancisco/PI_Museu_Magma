from rest_framework import viewsets, permissions
from .models import CustomUser
from .api_serializers import UserSerializer, UserCreateSerializer
from .api_permissions import IsAdminOrIsSelf

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = CustomUser.objects.all().order_by('-date_joined')
    permission_classes = [IsAdminOrIsSelf]

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the request action.
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer