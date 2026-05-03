"""
analytics/api_views.py

A single API view that aggregates all KPIs and returns them in one response.
"""

from datetime import date

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (
    get_product_data,
    get_revenue_data,
    get_sales_data,
    get_visitor_data,
)


def parse_date_param(value, param_name):
    """
    Converts a string like '2025-01-31' into a Python date object.
    """

    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(
            f"Invalid format for '{param_name}'. Expected YYYY-MM-DD, got '{value}'."
        )


@extend_schema(
    tags=["Analytics"],
    summary="Dashboard de KPIs",
    description=(
        "Retorna todos os indicadores-chave de desempenho do sistema em uma "
        "única requisição. Aceita filtros opcionais de período via query parameters."
    ),
    parameters=[
        OpenApiParameter(
            name="start_date",
            description="Data de início no formato YYYY-MM-DD. Ex: 2025-01-01",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="end_date",
            description="Data de fim no formato YYYY-MM-DD. Ex: 2025-12-31",
            required=False,
            type=str,
        ),
    ],
    responses={
        200: {
            "description": "KPIs agrupados por categoria.",
            "example": {
                "period": {
                    "start_date": None,
                    "end_date": None,
                },
                "revenue": {
                    "total": "15420.50",
                    "by_month": [
                        {
                            "month": "2025-01",
                            "revenue": "1200.00",
                        }
                    ],
                    "by_payment_method": [],
                },
                "sales": {
                    "total_count": 87,
                    "average_ticket": "177.24",
                    "total_discount": "320.00",
                },
                "products": {
                    "top_selling": [],
                    "low_stock": [],
                    "low_stock_count": 0,
                },
                "visitors": {
                    "total_count": 312,
                    "by_type": [],
                    "by_month": [],
                    "average_duration_minutes": 45,
                },
            },
        },
        400: {
            "description": "Parâmetro de data em formato inválido."
        },
    },
)
class DashboardView(APIView):
    """
    Returns all KPIs in a single request.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        try:
            start_date = parse_date_param(start_date_str, "start_date")
            end_date = parse_date_param(end_date_str, "end_date")
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_date and end_date and start_date > end_date:
            return Response(
                {"error": "'start_date' cannot be later than 'end_date'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {
            "period": {
                "start_date": str(start_date) if start_date else None,
                "end_date": str(end_date) if end_date else None,
            },
            "revenue": get_revenue_data(start_date, end_date),
            "sales": get_sales_data(start_date, end_date),
            "products": get_product_data(start_date, end_date),
            "visitors": get_visitor_data(start_date, end_date),
        }

        return Response(data, status=status.HTTP_200_OK)