from rest_framework import serializers

from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'created_at']  # Add created_at
        read_only_fields = ['id', 'created_at']  # Add created_at as read-only

    def create(self, validated_data):
        resume = Resume.objects.create(**validated_data)
        return resume
