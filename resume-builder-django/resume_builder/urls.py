from django.urls import path

from .views import ResumeCreateAPIView, ResumeUpdateAPIView

urlpatterns = [
    path('resumes/', ResumeCreateAPIView.as_view(), name='resume-create'),
    path('resumes/<uuid:pk>', ResumeUpdateAPIView.as_view(), name='resume-update'),
]
