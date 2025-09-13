from rest_framework import serializers

from .models import PersonalInformation, Resume


class PersonalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInformation
        fields = ['full_name', 'email', 'phone_number']


class ResumeSerializer(serializers.ModelSerializer):
    personal_information = PersonalInformationSerializer(required=False)

    class Meta:
        model = Resume
        fields = ['id', 'personal_information']  # , 'education', 'experience'
        read_only_fields = ['id']

    def create(self, validated_data):
        personal_info_data = validated_data.pop('personal_information', None)
        resume = Resume.objects.create(**validated_data)
        if personal_info_data:
            PersonalInformation.objects.create(resume=resume, **personal_info_data)
        return resume

    def update(self, instance, validated_data):
        personal_info_data = validated_data.pop('personal_information', None)

        # Update the Resume instance
        instance.save()

        if personal_info_data:
            # Check if a PersonalInformation object already exists for this resume
            personal_info_instance, created = PersonalInformation.objects.get_or_create(
                resume=instance
            )
            # If it already existed, update it; otherwise, it was just created
            for attr, value in personal_info_data.items():
                setattr(personal_info_instance, attr, value)
            personal_info_instance.save()

        return instance
