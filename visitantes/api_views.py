from django.shortcuts import render

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .api_serializers import (
    CheckInResponseSerializer,
    CheckInSerializer,
    CheckOutSerializer,
    VisitSerializer,
    VisitorSerializer,
)
from .models import Visit, Visitor


@extend_schema(tags=['Visitantes'])
class VisitorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing museum visitors.
    Supports full CRUD operations.
    """

    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]

    search_fields = ['name', 'document', 'email', 'phone']
    filterset_fields = ['visitor_type']

    @extend_schema(summary="Listar Visitantes")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Cadastrar Novo Visitante")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Consultar um Visitante")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Visitante (Completo)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Atualizar um Visitante (Parcial)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Excluir um Visitante")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(tags=['Visitas'])
class VisitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for managing museum visits.

    Read operations are available via standard list/retrieve.
    Check-in and check-out are handled via custom actions.
    """

    queryset = Visit.objects.all().select_related('visitor', 'registered_by')
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['visitor', 'registered_by']
    search_fields = ['visitor__name', 'notes']

    @extend_schema(summary="Listar Visitas")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Consultar uma Visita")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Realizar Check-in de Visitante",
        description=(
            "Registra a entrada de um visitante. Aceita um `visitor_id` existente "
            "ou os dados para cadastrar um novo visitante no momento do check-in. "
            "Retorna os dados da visita e o QR Code em base64."
        ),
        request=CheckInSerializer,
        responses={
            201: CheckInResponseSerializer,
            400: OpenApiResponse(description="Dados inválidos."),
            404: OpenApiResponse(description="Visitante não encontrado."),
        },
    )
    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        serializer = CheckInSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Resolve visitor: find existing or create new one
        if data.get('visitor_id'):
            try:
                visitor = Visitor.objects.get(pk=data['visitor_id'])
            except Visitor.DoesNotExist:
                return Response(
                    {'error': 'Visitante não encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            visitor = Visitor.objects.create(
                name=data['name'],
                document=data.get('document', ''),
                visitor_type=data.get('visitor_type', 'INDIVIDUAL'),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                created_by=request.user,
                updated_by=request.user,
            )

        visit = Visit.objects.create(
            visitor=visitor,
            companion_count=data.get('companion_count', 0),
            notes=data.get('notes', ''),
            registered_by=request.user,
        )

        response_serializer = CheckInResponseSerializer(visit)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Realizar Check-out de Visitante",
        description=(
            "Registra a saída de um visitante pelo `ticket_code` gerado no check-in. "
            "Retorna os dados completos da visita incluindo a duração em minutos."
        ),
        request=CheckOutSerializer,
        responses={
            200: VisitSerializer,
            400: OpenApiResponse(
                description="Dados inválidos ou visita já finalizada."
            ),
            404: OpenApiResponse(description="Ticket não encontrado."),
        },
    )
    @action(detail=False, methods=['post'], url_path='check-out')
    def check_out(self, request):
        serializer = CheckOutSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ticket_code = serializer.validated_data['ticket_code']

        try:
            visit = Visit.objects.select_related('visitor', 'registered_by').get(
                ticket_code=ticket_code
            )
        except Visit.DoesNotExist:
            return Response(
                {'error': 'Nenhuma visita encontrada com este ticket.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not visit.is_active:
            return Response(
                {'error': 'Esta visita já foi finalizada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        visit.check_out_at = timezone.now()
        visit.save()

        response_serializer = VisitSerializer(visit)
        return Response(response_serializer.data, status=status.HTTP_200_OK)