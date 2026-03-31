from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for reading user data.
    Password is excluded.
    """

    user_type_display = serializers.CharField(
        source='get_user_type_display', read_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'user_type',
            'user_type_display',
            'balance',
            'is_active',
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    Handles password hashing.
    """

    # Torna a password write-only (não pode ser lida) e obrigatória
    password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'user_type']

        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=validated_data.get('user_type', 'SELLER'),
        )
        return user
