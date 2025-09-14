from django.urls import path

from .views import ResumeCreateAPIView

urlpatterns = [
    path('resume/', ResumeCreateAPIView.as_view(), name='resume-create'),
]
