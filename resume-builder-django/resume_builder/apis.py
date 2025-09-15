from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import personal_information_get, resume_get
from .services import (
    personal_information_upsert,
    resume_create,
)

# RESUME


class ResumeCreateApi(APIView):
    """
    Returns Resume Instance from resume_id
    """

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def post(self, request):
        resume = resume_create()
        output_serializer = self.OutputSerializer(resume)
        return Response(data=output_serializer.data, status=status.HTTP_201_CREATED)


class ResumeReadApi(APIView):
    """
    Handles reading a new Resume Instance
    """

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def get(self, request, resume_id):
        resume = resume_get(resume_id=resume_id)
        output_serializer = self.OutputSerializer(resume)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


# PERSONAL INFO


class PersonalInformationUpsertApi(APIView):
    """
    Handles personal information for a resume.
    GET: Returns personal information for a resume
    PUT: Creates or updates personal information (upsert)
    """

    class InputSerializer(serializers.Serializer):
        full_name = serializers.CharField(
            max_length=100, required=False, allow_blank=True
        )
        email = serializers.EmailField(max_length=200, required=False, allow_blank=True)
        phone_number = serializers.CharField(
            max_length=20, required=False, allow_blank=True
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        full_name = serializers.CharField()
        email = serializers.EmailField()
        phone_number = serializers.CharField()
        resume_id = serializers.UUIDField(source='resume.id')
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def get(self, request, resume_id):
        personal_info = personal_information_get(resume_id=resume_id)
        output_serializer = self.OutputSerializer(personal_info)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, resume_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        personal_info = personal_information_upsert(
            resume_id=resume_id, **serializer.validated_data
        )
        output_serializer = self.OutputSerializer(personal_info)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)
