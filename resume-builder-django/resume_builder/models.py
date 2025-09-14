import uuid

from django.db import models
from django.utils import timezone

# Create your models here.


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Resume(BaseModel):
    pass


class PersonalInformation(BaseModel):
    full_name = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(max_length=200, blank=True, default='')
    phone_number = models.CharField(max_length=20, blank=True, default='')

    # one to one with resume
    resume = models.OneToOneField(
        Resume, on_delete=models.CASCADE, related_name='personal_info'
    )

    def __str__(self):
        return f'{self.full_name} - {self.email} - {self.phone_number}'
