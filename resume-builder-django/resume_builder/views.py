from rest_framework.generics import CreateAPIView

from .models import Resume
from .serializers import ResumeSerializer


class ResumeCreateAPIView(CreateAPIView):
    """
    Handles creating a new Resume Instance
    """

    serializer_class = ResumeSerializer
    queryset = Resume.objects.all()
