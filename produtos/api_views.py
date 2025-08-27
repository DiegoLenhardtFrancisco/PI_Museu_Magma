from rest_framework import viewsets, permissions
from produtos.models import Product
from .api_serializers import ProductSerializer

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

        serializer.save(user=self.request.user, code=next_code)
