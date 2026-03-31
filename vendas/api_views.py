from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets

from usuarios.api_permissions import IsAdminOrSaleOwner

from .api_serializers import CustomerSerializer, SaleItemReadSerializer, SaleSerializer
from .models import Customer, Sale, SaleItem


@extend_schema(tags=['Clientes'])
class CustomerViewSet(viewsets.ModelViewSet):
    """
    Endpoint for viewing and managing customers.

    **Permissions:**
    - Accessible to all authenticated users.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['customer_type']
    search_fields = ['name', 'document', 'email']

    @extend_schema(summary="Listar Clientes")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar um Novo Cliente")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Consultar um Cliente Específico")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Cliente (Completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Cliente (Parcial)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Excluir um Cliente")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

@extend_schema(tags=['Vendas'])
class SaleViewSet(viewsets.ModelViewSet):
    """
    Endpoint to view and manage sales.

    **Permissions:**
    - `ADMIN` can view and manage all sales.
    - `SELLER` can create sales and view/manage only their own sales.
    """

    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAdminOrSaleOwner]

    filterset_fields = ['customer', 'status', 'payment_method', 'created_by']
    search_fields = ['customer__name', 'created_by__username', 'notes', 'id']

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

    @extend_schema(summary="Listar Vendas")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar uma Nova Venda")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Consultar uma Venda Específica")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar uma Venda (Completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar uma Venda (Parcial)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Excluir uma Venda")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

@extend_schema(tags=['Vendas'])
class SaleItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint to view the items in a sale.
    """
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Listar todos os Itens de Venda")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Consultar um Item de Venda Específico")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)