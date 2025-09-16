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


class Education(BaseModel):
    degree = models.CharField(max_length=200)
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)

    # many to one relationship with resume
    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name='education_records'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.degree}'


class Experience(BaseModel):
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)

    # many to one relationship with resume
    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name='experience_records'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.company} - {self.position}'
