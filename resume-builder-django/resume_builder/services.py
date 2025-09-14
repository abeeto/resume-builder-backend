# services.py - where business logic involving pushing to DB/backend
from .models import PersonalInformation, Resume


def resume_create() -> Resume:
    """
    Creates a new resume instance
    """
    resume = Resume()
    resume.full_clean()
    resume.save()

    return resume


def personal_information_create(
    *, resume_id: str, full_name: str = '', email: str = '', phone_number: str = ''
) -> PersonalInformation:
    """
    Creates personal information for resume
    """
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        raise ValueError(f'Resume with id {resume_id} does not exist')

    if hasattr(resume, 'personal_info'):
        raise ValueError('Personal information already exists')

    personal_info = PersonalInformation(
        resume=resume, full_name=full_name, email=email, phone_number=phone_number
    )

    personal_info.save()

    return personal_info
