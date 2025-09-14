from django.urls import path

from .apis import PersonalInformationCreateApi, ResumeCreateApi

urlpatterns = [
    path('resume/', ResumeCreateApi.as_view(), name='resume-create'),
    path(
        'resume/<uuid:resume_id>/personal-info/',
        PersonalInformationCreateApi.as_view(),
        name='personal-info-create',
    ),
]
