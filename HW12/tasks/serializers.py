from django.utils import timezone
from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи: title, description, status, deadline."""

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "deadline", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_deadline(self, value):
        """Дедлайн новой задачи не может быть в прошлом."""
        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом.")
        return value
