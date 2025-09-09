from rest_framework import permissions, viewsets

from produtos.models import Product

from .api_serializers import ProductSerializer, StockMovementSerializer
from .models import StockMovement
from usuarios.api_permissions import IsAdminOrStocker 
from drf_spectacular.utils import extend_schema, OpenApiResponse

@extend_schema(tags=['Produtos'])
class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """

    queryset = Product.objects.filter(is_active=True).order_by('name')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrStocker]

    filterset_fields = ['category', 'supplier', 'is_active']
    search_fields = ['name', 'description', 'code']

    @extend_schema(
        summary="Listar Produtos",
        description="Retorna uma lista paginada de todos os produtos ativos. Acesso de leitura para todos os usuários autenticados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Criar um Novo Produto",
        description="Cria um novo produto no sistema. Apenas usuários do tipo `ADMIN` ou `STOCKCLERK` podem executar esta ação.",
        responses={
            201: OpenApiResponse(description="Produto criado com sucesso."),
            400: OpenApiResponse(description="Erro de validação nos dados enviados."),
            403: OpenApiResponse(description="Acesso negado. O usuário não tem permissão para criar produtos.")
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Consultar um Produto")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Produto (Completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Produto (Parcial)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Excluir um Produto")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

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

@extend_schema(tags=['Estoque'])
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

    @extend_schema(
        summary="Listar Movimentações de Estoque",
        description="Retorna um histórico de todas as movimentações de estoque (entradas, saídas e ajustes)."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Consultar uma Movimentação de Estoque")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
