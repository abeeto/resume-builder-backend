from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import resume_create


class ResumeCreateApi(APIView):
    """
    Handles creating a new Resume Instance
    """

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def post(self, request):
        resume = resume_create()

        output_serializer = self.OutputSerializer(resume)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
