from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema(tags=['Monitoramento'])
class HealthCheckView(APIView):
    """
    A simple view to check if the API is operational.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        Returns a 200 OK status with a simple message.
        """
        return Response({"status": "ok"}, status=status.HTTP_200_OK)