from django.db.models import Q, Sum
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .api_serializers import FixedCostEntrySerializer, FixedCostSummarySerializer
from .models import FixedCostEntry


@extend_schema(tags=['Custos Fixos'])
class FixedCostEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing fixed cost entries.

    Supports full CRUD plus a summary action that returns aggregated totals.

    Filters (via query parameters):
    - ?month=YYYY-MM   → entries whose due_date falls in that month
    - ?category=RENT   → entries of a specific category
    - ?status=PENDING  → entries with a specific status
    """

    serializer_class = FixedCostEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    # Fields available for ?search= queries
    search_fields = ['description']

    # Fields available for exact ?field=value filters
    filterset_fields = ['category', 'status']

    def get_queryset(self):
        """
        Returns entries filtered by the optional ?month= query parameter.

        If ?month=2026-04 is provided, only entries with due_date in April 2026
        are returned. Without it, all entries are returned.
        """
        qs = FixedCostEntry.objects.all()

        month_param = self.request.query_params.get('month')
        if month_param:
            try:
                # month_param expected as "YYYY-MM"
                year, month = month_param.split('-')
                qs = qs.filter(due_date__year=int(year), due_date__month=int(month))
            except (ValueError, AttributeError):
                # Invalid format — ignore the filter, return unfiltered
                pass

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    # --- Standard CRUD with Swagger descriptions ---

    @extend_schema(
        summary="Listar Custos Fixos",
        description=(
            "Retorna a lista de custos fixos. "
            "Aceita filtros por `month` (YYYY-MM), `category` e `status`."
        ),
        parameters=[
            OpenApiParameter(
                name='month',
                description='Mês de vencimento no formato YYYY-MM (ex: 2026-04)',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='category',
                description='Código da categoria (ex: RENT, ELECTRICITY, TAXES)',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='status',
                description='Status do custo: PENDING ou PAID',
                required=False,
                type=str,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Criar Custo Fixo")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Consultar um Custo Fixo")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Custo Fixo (Completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Custo Fixo (Parcial)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Excluir um Custo Fixo")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # --- Custom action: totals summary ---

    @extend_schema(
        summary="Resumo de Totais",
        description=(
            "Retorna os totais agregados: total pendente, total pago e total geral. "
            "Respeita os mesmos filtros de `month`, `category` e `status` do list."
        ),
        responses={
            200: OpenApiResponse(
                description="Totais calculados sobre o queryset filtrado.",
                response=FixedCostSummarySerializer,
            )
        },
    )
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Returns total_pending, total_paid and total_overall for the current filter.

        The same ?month= and ?category= filters applied on list() also affect
        this endpoint, because we reuse get_queryset().
        """
        qs = self.get_queryset()

        # Apply category/status filterset manually since @action bypasses it
        category = request.query_params.get('category')
        status_param = request.query_params.get('status')
        if category:
            qs = qs.filter(category=category)
        if status_param:
            qs = qs.filter(status=status_param)

        totals = qs.aggregate(
            total_pending=Sum('value', filter=Q(status=FixedCostEntry.Status.PENDING)),
            total_paid=Sum('value', filter=Q(status=FixedCostEntry.Status.PAID)),
            total_overall=Sum('value'),
        )

        data = {
            'total_pending': totals['total_pending'] or 0,
            'total_paid': totals['total_paid'] or 0,
            'total_overall': totals['total_overall'] or 0,
        }

        serializer = FixedCostSummarySerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)
