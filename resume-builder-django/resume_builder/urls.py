from django.urls import path

from .apis import ResumeCreateApi

urlpatterns = [
    path('resume/', ResumeCreateApi.as_view(), name='resume-create'),
]
