# services.py - where business logic involving pushing to DB/backend

from .models import Resume


def resume_create() -> Resume:
    """
    Creates a new resume instance
    """
    resume = Resume()
    resume.full_clean()
    resume.save()

    return resume
