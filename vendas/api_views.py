from rest_framework import viewsets, permissions
from .models import Customer, Sale, SaleItem
from .api_serializers import CustomerSerializer, SaleSerializer, SaleItemReadSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['customer_type']
    search_fields = ['name', 'document', 'email']

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['customer', 'status', 'payment_method', 'user']
    search_fields = ['notes']

    def get_serializer_context(self):
        return {'request': self.request}
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, code=next_code) 

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class SaleItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemReadSerializer
    permission_classes = [permissions.IsAuthenticated]