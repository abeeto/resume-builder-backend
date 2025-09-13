import uuid

from django.db import models

# Create your models here.


class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Resume {self.id}'


class PersonalInformation(models.Model):
    resume = models.OneToOneField(
        Resume, on_delete=models.CASCADE, related_name='personal_information'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'Personal info for {self.resume.id}, name: {self.resume.full_name}'
