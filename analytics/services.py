"""
analytics/services.py

This module contains all the database query logic for the analytics dashboard.
"""

from django.db.models import (
    Avg,
    Count,
    DecimalField,
    DurationField,
    ExpressionWrapper,
    F,
    Sum,
)
from django.db.models.functions import TruncMonth

from produtos.models import Product
from vendas.models import Sale, SaleItem
from visitantes.models import Visit


def get_date_filters(start_date, end_date):
    filters = {}

    if start_date:
        filters['gte'] = start_date

    if end_date:
        filters['lte'] = end_date

    return filters


def get_revenue_data(start_date=None, end_date=None):
    sales_qs = Sale.objects.filter(status='COMPLETED')

    if start_date:
        sales_qs = sales_qs.filter(sale_date__date__gte=start_date)

    if end_date:
        sales_qs = sales_qs.filter(sale_date__date__lte=end_date)

    total_result = sales_qs.aggregate(total=Sum('total_amount'))
    total_revenue = total_result['total'] or 0

    by_month = (
        sales_qs.annotate(month=TruncMonth('sale_date'))
        .values('month')
        .annotate(revenue=Sum('total_amount'))
        .order_by('month')
    )

    by_month_list = [
        {
            'month': entry['month'].strftime('%Y-%m'),
            'revenue': f"{entry['revenue'] or 0:.2f}",
        }
        for entry in by_month
        if entry['month'] is not None
    ]

    by_payment = (
        sales_qs.values('payment_method')
        .annotate(revenue=Sum('total_amount'), count=Count('id'))
        .order_by('-revenue')
    )

    payment_labels = dict(Sale.PAYMENT_METHOD_CHOICES)

    by_payment_list = [
        {
            'method': entry['payment_method'],
            'method_display': payment_labels.get(
                entry['payment_method'],
                entry['payment_method'],
            ),
            'revenue': f"{entry['revenue'] or 0:.2f}",
            'count': entry['count'],
        }
        for entry in by_payment
    ]

    return {
        'total': f'{total_revenue:.2f}',
        'by_month': by_month_list,
        'by_payment_method': by_payment_list,
    }


def get_sales_data(start_date=None, end_date=None):
    sales_qs = Sale.objects.filter(status='COMPLETED')

    if start_date:
        sales_qs = sales_qs.filter(sale_date__date__gte=start_date)

    if end_date:
        sales_qs = sales_qs.filter(sale_date__date__lte=end_date)

    result = sales_qs.aggregate(
        total_count=Count('id'),
        average_ticket=Avg('total_amount'),
        total_discount=Sum('discount'),
    )

    return {
        'total_count': result['total_count'] or 0,
        'average_ticket': str(round(result['average_ticket'] or 0, 2)),
        'total_discount': str(result['total_discount'] or 0),
    }


def get_product_data(start_date=None, end_date=None):
    sale_items_qs = SaleItem.objects.filter(sale__status='COMPLETED')

    if start_date:
        sale_items_qs = sale_items_qs.filter(sale__sale_date__date__gte=start_date)

    if end_date:
        sale_items_qs = sale_items_qs.filter(sale__sale_date__date__lte=end_date)

    top_selling = (
        sale_items_qs.values('product__id', 'product__name', 'product__category')
        .annotate(
            total_quantity_sold=Sum('quantity'),
            total_revenue=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price'),
                    output_field=DecimalField(),
                )
            ),
        )
        .order_by('-total_quantity_sold')[:10]
    )

    top_selling_list = [
        {
            'product_id': entry['product__id'],
            'product_name': entry['product__name'],
            'category': entry['product__category'],
            'total_quantity_sold': str(entry['total_quantity_sold'] or 0),
            'total_revenue': str(entry['total_revenue'] or 0),
        }
        for entry in top_selling
    ]

    low_stock = (
        Product.objects.filter(is_active=True, quantity__lte=F('minimum_quantity'))
        .values('id', 'name', 'quantity', 'minimum_quantity', 'category')
        .order_by('quantity')[:20]
    )

    low_stock_list = [
        {
            'product_id': entry['id'],
            'product_name': entry['name'],
            'current_quantity': str(entry['quantity']),
            'minimum_quantity': str(entry['minimum_quantity']),
            'category': entry['category'],
        }
        for entry in low_stock
    ]

    return {
        'top_selling': top_selling_list,
        'low_stock': low_stock_list,
        'low_stock_count': len(low_stock_list),
    }


def get_visitor_data(start_date=None, end_date=None):
    visits_qs = Visit.objects.all()

    if start_date:
        visits_qs = visits_qs.filter(check_in_at__date__gte=start_date)

    if end_date:
        visits_qs = visits_qs.filter(check_in_at__date__lte=end_date)

    total_count = visits_qs.count()

    by_type = (
        visits_qs.values('visitor__visitor_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    visitor_type_labels = {
        'INDIVIDUAL': 'Individual',
        'GROUP': 'Grupo',
        'SCHOOL': 'Grupo Escolar',
        'GUIDED': 'Tour Guiado',
    }

    by_type_list = [
        {
            'type': entry['visitor__visitor_type'],
            'type_display': visitor_type_labels.get(
                entry['visitor__visitor_type'],
                entry['visitor__visitor_type'],
            ),
            'count': entry['count'],
        }
        for entry in by_type
    ]

    by_month = (
        visits_qs.annotate(month=TruncMonth('check_in_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    by_month_list = [
        {
            'month': entry['month'].strftime('%Y-%m'),
            'count': entry['count'],
        }
        for entry in by_month
        if entry['month'] is not None
    ]

    completed_visits = visits_qs.filter(check_out_at__isnull=False)

    avg_duration_result = completed_visits.aggregate(
        avg_duration=Avg(
            ExpressionWrapper(
                F('check_out_at') - F('check_in_at'),
                output_field=DurationField(),
            )
        )
    )

    avg_duration = avg_duration_result['avg_duration']
    avg_duration_minutes = (
        int(avg_duration.total_seconds() / 60) if avg_duration else None
    )

    return {
        'total_count': total_count,
        'by_type': by_type_list,
        'by_month': by_month_list,
        'average_duration_minutes': avg_duration_minutes,
    }
