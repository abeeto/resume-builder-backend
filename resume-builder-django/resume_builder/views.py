from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PersonalInformation, Resume
from .serializers import PersonalInformationSerializer, ResumeSerializer


class ResumeCreateAPIView(APIView):
    """
    Handles creating a new Resume Instance
    """

    def post(self, request, *args, **kwargs):
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResumeUpdateAPIView(APIView):
    """
    Hanldes the autosave/update by referring to the UUID
    """

    def get(self, request, pk, *args, **kwargs):
        resume = get_object_or_404(Resume, pk=pk)
        serializer = ResumeSerializer(resume)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        resume = get_object_or_404(Resume, pk=pk)
        personal_info_data = request.data.get('personal_information')

        if personal_info_data is None:
            try:
                personal_info = resume.personal_information
                resume.personal_information.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except PersonalInformation.DoesNotExist:
                return Response(status=status.HTTP_204_NO_CONTENT)

        personal_info, created = PersonalInformation.objects.get_or_create(
            resume=resume
        )
        serializer = PersonalInformationSerializer(
            personal_info, data=personal_info_data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
