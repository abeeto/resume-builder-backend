# services.py - where business logic involving pushing to DB/backend
from .models import Education, Experience, PersonalInformation, Resume


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


def personal_information_update(
    *,
    personal_info_id: str,
    full_name: str = None,
    email: str = None,
    phone_number: str = None,
) -> PersonalInformation:
    """
    Updates personal information fields.
    Only updates fields that are provided (not None).
    """
    try:
        personal_info = PersonalInformation.objects.get(id=personal_info_id)
    except PersonalInformation.DoesNotExist:
        raise ValueError(
            f'Personal information with id {personal_info_id} does not exist'
        )

    if full_name is not None:
        personal_info.full_name = full_name
    if email is not None:
        personal_info.email = email
    if phone_number is not None:
        personal_info.phone_number = phone_number

    personal_info.full_clean()
    personal_info.save()

    return personal_info


def personal_information_upsert(
    *, resume_id: str, full_name: str = '', email: str = '', phone_number: str = ''
) -> PersonalInformation:
    """
    Creates or updates personal information for a resume.
    If personal information already exists, it updates it.
    If it doesn't exist, it creates new personal information.
    """
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        raise ValueError(f'Resume with id {resume_id} does not exist')

    try:
        personal_info = resume.personal_info
        personal_info.full_name = full_name
        personal_info.email = email
        personal_info.phone_number = phone_number
        personal_info.full_clean()
        personal_info.save()
        return personal_info
    except PersonalInformation.DoesNotExist:
        personal_info = PersonalInformation(
            resume=resume, full_name=full_name, email=email, phone_number=phone_number
        )
        personal_info.full_clean()
        personal_info.save()
        return personal_info


def education_create(
    *,
    resume_id: str,
    degree: str = '',
    start_date: str = '',
    end_date: str = '',
    location: str = '',
) -> Education:
    """
    Creates education record for resume
    """
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        raise ValueError(f'Resume with id {resume_id} does not exist')

    education = Education(
        resume=resume,
        degree=degree,
        start_date=start_date,
        end_date=end_date,
        location=location,
    )
    education.full_clean()
    education.save()
    return education


def education_update(
    *,
    education_id: str,
    degree: str = '',
    start_date: str = '',
    end_date: str = '',
    location: str = '',
) -> Education:
    """
    Updates education record.
    """
    try:
        education = Education.objects.get(id=education_id)
    except Education.DoesNotExist:
        raise ValueError(f'Education with id {education_id} does not exist')

    education.degree = degree
    education.start_date = start_date
    education.end_date = end_date
    education.location = location
    education.full_clean()
    education.save()
    return education


def education_delete(*, education_id: str) -> None:
    """
    Deletes education record by id
    """
    try:
        education = Education.objects.get(id=education_id)
    except Education.DoesNotExist:
        raise ValueError(f'Education with id {education_id} does not exist')

    education.delete()


def experience_create(
    *,
    resume_id: str,
    company: str = '',
    position: str = '',
    description: str = '',
    start_date: str = '',
    end_date: str = '',
    location: str = '',
) -> Experience:
    """
    Creates experience record for resume
    """
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        raise ValueError(f'Resume with id {resume_id} does not exist')

    experience = Experience(
        resume=resume,
        company=company,
        position=position,
        description=description,
        start_date=start_date,
        end_date=end_date,
        location=location,
    )
    experience.full_clean()
    experience.save()
    return experience


def experience_update(
    *,
    experience_id: str,
    company: str = '',
    position: str = '',
    description: str = '',
    start_date: str = '',
    end_date: str = '',
    location: str = '',
) -> Experience:
    """
    Updates experience record.
    """
    try:
        experience = Experience.objects.get(id=experience_id)
    except Experience.DoesNotExist:
        raise ValueError(f'Experience with id {experience_id} does not exist')

    experience.company = company
    experience.position = position
    experience.description = description
    experience.start_date = start_date
    experience.end_date = end_date
    experience.location = location
    experience.full_clean()
    experience.save()
    return experience


def experience_delete(*, experience_id: str) -> None:
    """
    Deletes experience record by id
    """
    try:
        experience = Experience.objects.get(id=experience_id)
    except Experience.DoesNotExist:
        raise ValueError(f'Experience with id {experience_id} does not exist')

    experience.delete()
