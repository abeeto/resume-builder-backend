from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import (
    education_list,
    experience_list,
    personal_information_get,
    resume_get,
)
from .services import (
    education_create,
    education_delete,
    education_update,
    experience_create,
    experience_delete,
    experience_update,
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
        try:
            personal_info = personal_information_get(resume_id=resume_id)
        except ValueError as e:
            if 'Personal information for resume' in str(e) and 'does not exist' in str(
                e
            ):
                personal_info = personal_information_upsert(resume_id=resume_id)
            else:
                raise e
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


# EDUCATION


class EducationListApi(APIView):
    """
    GET: Returns all education records for a resume
    POST: Creates new education for a resume
    """

    class InputSerializer(serializers.Serializer):
        degree = serializers.CharField(max_length=200, required=False, allow_blank=True)
        start_date = serializers.CharField(
            max_length=50, required=False, allow_blank=True
        )
        end_date = serializers.CharField(
            max_length=50, required=False, allow_blank=True
        )
        location = serializers.CharField(
            max_length=100, required=False, allow_blank=True
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        degree = serializers.CharField()
        start_date = serializers.CharField()
        end_date = serializers.CharField()
        location = serializers.CharField()
        resume_id = serializers.UUIDField(source='resume.id')
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def get(self, request, resume_id):
        education_records = education_list(resume_id=resume_id)
        output_serializer = self.OutputSerializer(education_records, many=True)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, resume_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        education = education_create(resume_id=resume_id, **serializer.validated_data)
        output_serializer = self.OutputSerializer(education)
        return Response(data=output_serializer.data, status=status.HTTP_201_CREATED)


class EducationUpdateApi(APIView):
    """
    PUT: Updates existing education
    """

    class InputSerializer(serializers.Serializer):
        degree = serializers.CharField(max_length=200, required=False, allow_blank=True)
        start_date = serializers.CharField(
            max_length=50, required=False, allow_blank=True
        )
        end_date = serializers.CharField(
            max_length=50, required=False, allow_blank=True
        )
        location = serializers.CharField(
            max_length=100, required=False, allow_blank=True
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        degree = serializers.CharField()
        start_date = serializers.CharField()
        end_date = serializers.CharField()
        location = serializers.CharField()
        resume_id = serializers.UUIDField(source='resume.id')
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def put(self, request, education_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        education = education_update(
            education_id=education_id, **serializer.validated_data
        )
        output_serializer = self.OutputSerializer(education)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)


class EducationDeleteApi(APIView):
    """
    DELETE: Deletes existing education
    """

    def delete(self, request, education_id):
        education_delete(education_id=education_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


# EXPERIENCE


class ExperienceListApi(APIView):
    """
    GET: Returns all experience records for a resume
    POST: Creates new experience for a resume
    """

    class InputSerializer(serializers.Serializer):
        company = serializers.CharField(
            max_length=200, required=False, allow_blank=True
        )
        position = serializers.CharField(
            max_length=200, required=False, allow_blank=True
        )
        description = serializers.CharField(required=False, allow_blank=True)
        start_date = serializers.CharField(
            max_length=50, required=False, allow_blank=True
        )
        end_date = serializers.CharField(
            max_length=50, required=False, allow_blank=True
        )
        location = serializers.CharField(
            max_length=100, required=False, allow_blank=True
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        company = serializers.CharField()
        position = serializers.CharField()
        description = serializers.CharField()
        start_date = serializers.CharField()
        end_date = serializers.CharField()
        location = serializers.CharField()
        resume_id = serializers.UUIDField(source='resume.id')
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def get(self, request, resume_id):
        experience_records = experience_list(resume_id=resume_id)
        output_serializer = self.OutputSerializer(experience_records, many=True)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, resume_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        experience = experience_create(resume_id=resume_id, **serializer.validated_data)
        output_serializer = self.OutputSerializer(experience)
        return Response(data=output_serializer.data, status=status.HTTP_201_CREATED)


class ExperienceUpdateApi(APIView):
    """
    PUT: Updates existing experience
    """

    class InputSerializer(serializers.Serializer):
        company = serializers.CharField(
            max_length=200, required=False, allow_blank=True
        )
        position = serializers.CharField(
            max_length=200, required=False, allow_blank=True
        )
        description = serializers.CharField(required=False, allow_blank=True)
        start_date = serializers.CharField(
            max_length=50, required=False, allow_blank=True
        )
        end_date = serializers.CharField(
            max_length=50, required=False, allow_blank=True
        )
        location = serializers.CharField(
            max_length=100, required=False, allow_blank=True
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        company = serializers.CharField()
        position = serializers.CharField()
        description = serializers.CharField()
        start_date = serializers.CharField()
        end_date = serializers.CharField()
        location = serializers.CharField()
        resume_id = serializers.UUIDField(source='resume.id')
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def put(self, request, experience_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        experience = experience_update(
            experience_id=experience_id, **serializer.validated_data
        )
        output_serializer = self.OutputSerializer(experience)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)


class ExperienceDeleteApi(APIView):
    """
    DELETE: Deletes existing experience
    """

    def delete(self, request, experience_id):
        experience_delete(experience_id=experience_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
