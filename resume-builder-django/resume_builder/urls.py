from django.urls import path

from .apis import (
    EducationDeleteApi,
    EducationListApi,
    EducationUpdateApi,
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
    path(
        'resume/<uuid:resume_id>/education/',
        EducationListApi.as_view(),
        name='education-list',
    ),
    path(
        'education/<uuid:education_id>/',
        EducationUpdateApi.as_view(),
        name='education-update',
    ),
    path(
        'education/<uuid:education_id>/delete/',
        EducationDeleteApi.as_view(),
        name='education-delete',
    ),
]
