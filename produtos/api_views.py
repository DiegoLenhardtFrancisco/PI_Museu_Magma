from rest_framework import permissions, viewsets

from produtos.models import Product

from .api_serializers import ProductSerializer, StockMovementSerializer
from .models import StockMovement


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """

    queryset = Product.objects.filter(is_active=True).order_by('name')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['category', 'supplier', 'is_active']
    search_fields = ['name', 'description', 'code']

    def perform_create(self, serializer):
        last_product = Product.objects.order_by('-code').first()
        if last_product and last_product.code.isdigit():
            next_code = str(int(last_product.code) + 1).zfill(6)
        else:
            next_code = '000001'

        serializer.save(
            created_by=self.request.user, updated_by=self.request.user, code=next_code
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only API endpoint for viewing stock movements.

    Stock movements are created automatically by signals when products are
    created or updated, so this endpoint does not allow creation or deletion.
    """

    queryset = StockMovement.objects.all().select_related('product', 'user')
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['product', 'type', 'user']
    search_fields = ['product__name', 'user__username', 'notes']
