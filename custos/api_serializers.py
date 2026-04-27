from datetime import date

from rest_framework import serializers

from .models import FixedCostEntry


class FixedCostEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for FixedCostEntry.

    Extra read-only fields:
    - category_display: human-readable category label (e.g. "Aluguel")
    - status_display:   human-readable status label   (e.g. "Pendente")
    - is_overdue:       True when status=PENDING and due_date is in the past
    """

    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = FixedCostEntry
        fields = [
            'id',
            'category',
            'category_display',
            'description',
            'value',
            'due_date',
            'paid_at',
            'status',
            'status_display',
            'is_overdue',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = [
            'id',
            'paid_at',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]

    def get_is_overdue(self, obj):
        """
        An entry is overdue when it is still pending AND its due date has passed.
        This flag lets the frontend apply the stronger red highlight.
        """
        return obj.status == FixedCostEntry.Status.PENDING and obj.due_date < date.today()

    def update(self, instance, validated_data):
        """
        When status changes to PAID, automatically record today as paid_at.
        When status changes back to PENDING, clear paid_at.
        """
        new_status = validated_data.get('status', instance.status)

        if new_status == FixedCostEntry.Status.PAID and instance.status != new_status:
            validated_data['paid_at'] = date.today()

        if new_status == FixedCostEntry.Status.PENDING:
            validated_data['paid_at'] = None

        return super().update(instance, validated_data)


class FixedCostSummarySerializer(serializers.Serializer):
    """
    Read-only serializer for the aggregated totals returned alongside the list.
    This is only used for Swagger documentation — the data is built manually
    in the view using Django ORM aggregation.
    """

    total_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_overall = serializers.DecimalField(max_digits=12, decimal_places=2)