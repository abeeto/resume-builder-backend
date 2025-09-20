# selectors.py - where business logic involving pulling from DB/backend
from .models import PersonalInformation, Resume


def personal_information_get(*, resume_id: str) -> PersonalInformation:
    """
    Gets personal information for a resume by resume_id
    """
    try:
        resume = Resume.objects.select_related('personal_info').get(id=resume_id)
    except Resume.DoesNotExist:
        raise ValueError(f'Resume with id {resume_id} does not exist')

    try:
        return resume.personal_info
    except PersonalInformation.DoesNotExist:
        raise ValueError(f'Personal information for resume {resume_id} does not exist')


def resume_get(*, resume_id: str) -> Resume:
    """
    Gets resume record by resume_id
    """
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        raise ValueError(f'Resume with id {resume_id} does not exist')
    return resume


def education_list(*, resume_id: str):
    """
    Gets all education records for a resume by resume_id
    """
    try:
        resume = Resume.objects.prefetch_related('education_records').get(id=resume_id)
    except Resume.DoesNotExist:
        raise ValueError(f'Resume with id {resume_id} does not exist')

    return resume.education_records.all()


def experience_list(*, resume_id: str):
    """
    Gets all experience records for a resume by resume_id
    """
    try:
        resume = Resume.objects.prefetch_related('experience_records').get(id=resume_id)
    except Resume.DoesNotExist:
        raise ValueError(f'Resume with id {resume_id} does not exist')

    return resume.experience_records.all()
