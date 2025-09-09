from rest_framework import permissions, viewsets

from .api_serializers import CustomerSerializer, SaleItemReadSerializer, SaleSerializer
from .models import Customer, Sale, SaleItem
from usuarios.api_permissions import IsAdminOrSaleOwner
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Clientes'])
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['customer_type']
    search_fields = ['name', 'document', 'email']

@extend_schema(tags=['Vendas'])
class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAdminOrSaleOwner]

    filterset_fields = ['customer', 'status', 'payment_method', 'created_by']
    search_fields = ['notes']

    def get_queryset(self):
        """
        Admins see all sales.
        Other users (Sellers) only see their own sales.
        """
        user = self.request.user
        if user.is_staff or user.user_type == 'ADMIN':
            return Sale.objects.all()
        return Sale.objects.filter(created_by=user)

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

@extend_schema(tags=['Vendas'])
class SaleItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemReadSerializer
    permission_classes = [permissions.IsAuthenticated]
