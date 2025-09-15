from django.urls import path

from .apis import (
    PersonalInformationUpsertApi,
    ResumeCreateApi,
    ResumeReadApi,
)

urlpatterns = [
    path('resume/create/', ResumeCreateApi.as_view(), name='resume-create'),
    path('resume/<uuid:resume_id>/', ResumeReadApi.as_view(), name='resume-read'),
    path(
        'resume/<uuid:resume_id>/personal-info/',
        PersonalInformationUpsertApi.as_view(),
        name='personal-info-upsert',
    ),
]
