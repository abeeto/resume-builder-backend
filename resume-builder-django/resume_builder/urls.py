from django.urls import path

from .apis import (
    EducationDeleteApi,
    EducationListApi,
    EducationUpdateApi,
    ExperienceDeleteApi,
    ExperienceListApi,
    ExperienceUpdateApi,
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
    path(
        'resume/<uuid:resume_id>/experience/',
        ExperienceListApi.as_view(),
        name='experience-list',
    ),
    path(
        'experience/<uuid:experience_id>/',
        ExperienceUpdateApi.as_view(),
        name='experience-update',
    ),
    path(
        'experience/<uuid:experience_id>/delete/',
        ExperienceDeleteApi.as_view(),
        name='experience-delete',
    ),
]
