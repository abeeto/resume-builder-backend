from django.urls import path

from .apis import (
    PersonalInformationCreateApi,
    PersonalInformationReadApi,
    PersonalInformationUpdateApi,
    ResumeCreateApi,
    ResumeReadApi,
)

urlpatterns = [
    path('resume/create/', ResumeCreateApi.as_view(), name='resume-create'),
    path('resume/<uuid:resume_id>/', ResumeReadApi.as_view(), name='resume-read'),
    path(
        'resume/<uuid:resume_id>/personal-info/create/',
        PersonalInformationCreateApi.as_view(),
        name='personal-info-create',
    ),
    path(
        'resume/<uuid:resume_id>/personal-info/',
        PersonalInformationReadApi.as_view(),
        name='personal-info-read',
    ),
    path(
        'personal-info/<uuid:personal_info_id>/update/',
        PersonalInformationUpdateApi.as_view(),
        name='personal-info-update',
    ),
]
