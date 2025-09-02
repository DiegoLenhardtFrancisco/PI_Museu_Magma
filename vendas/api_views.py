from rest_framework import viewsets, permissions
from .models import Customer, Sale, SaleItem
from .api_serializers import CustomerSerializer, SaleSerializer, SaleItemReadSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        # Passa o 'request' para o serializer para que possamos obter o 'user'
        return {'request': self.request}

class SaleItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemReadSerializer
    permission_classes = [permissions.IsAuthenticated]