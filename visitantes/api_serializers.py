import base64
import io

import qrcode
from rest_framework import serializers

from .models import Visit, Visitor


def generate_qr_code_base64(data: str) -> str:
    """
    Generates a QR Code image from a string and returns it
    as a base64-encoded PNG string.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


class VisitorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Visitor model.
    Includes a computed field with total visit count.
    """

    visitor_type_display = serializers.CharField(
        source='get_visitor_type_display', read_only=True
    )
    total_visits = serializers.SerializerMethodField()

    class Meta:
        model = Visitor
        fields = [
            'id',
            'name',
            'document',
            'visitor_type',
            'visitor_type_display',
            'email',
            'phone',
            'notes',
            'total_visits',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_visits(self, obj):
        return obj.visits.count()


class VisitSerializer(serializers.ModelSerializer):
    """
    Serializer for the Visit model. Used for listing and detail views.
    """

    visitor_name = serializers.CharField(source='visitor.name', read_only=True)
    visitor_type_display = serializers.CharField(
        source='visitor.get_visitor_type_display', read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)
    registered_by_name = serializers.CharField(
        source='registered_by.username', read_only=True, default='Sistema'
    )

    class Meta:
        model = Visit
        fields = [
            'id',
            'visitor',
            'visitor_name',
            'visitor_type_display',
            'ticket_code',
            'check_in_at',
            'check_out_at',
            'companion_count',
            'notes',
            'is_active',
            'duration_minutes',
            'registered_by',
            'registered_by_name',
        ]
        read_only_fields = [
            'id',
            'ticket_code',
            'check_in_at',
            'registered_by',
        ]


class CheckInSerializer(serializers.Serializer):
    """
    Input serializer for the check-in action.
    Accepts either an existing visitor_id or data to create a new visitor.
    """

    # Option A: reference an existing visitor
    visitor_id = serializers.IntegerField(required=False)

    # Option B: create a new visitor on the spot
    name = serializers.CharField(max_length=150, required=False)
    document = serializers.CharField(max_length=20, required=False, allow_blank=True)
    visitor_type = serializers.ChoiceField(
        choices=['INDIVIDUAL', 'GROUP', 'SCHOOL', 'GUIDED'],
        required=False,
        default='INDIVIDUAL',
    )
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # Visit-specific fields
    companion_count = serializers.IntegerField(min_value=0, default=0)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('visitor_id') and not data.get('name'):
            raise serializers.ValidationError(
                "Either 'visitor_id' or visitor 'name' must be provided."
            )
        return data


class CheckInResponseSerializer(serializers.ModelSerializer):
    """
    Output serializer for the check-in response.
    Includes the generated QR Code as a base64 string.
    """

    visitor_name = serializers.CharField(source='visitor.name', read_only=True)
    qr_code_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = [
            'id',
            'visitor',
            'visitor_name',
            'ticket_code',
            'check_in_at',
            'companion_count',
            'notes',
            'qr_code_base64',
        ]

    def get_qr_code_base64(self, obj):
        return generate_qr_code_base64(str(obj.ticket_code))


class CheckOutSerializer(serializers.Serializer):
    """Input serializer for the check-out action."""

    ticket_code = serializers.UUIDField()
