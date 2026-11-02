from django.utils import timezone
from rest_framework import serializers

from .models import Category, SubTask, Task


# ---------------------------------------------------------------------------
# Подзадачи
# ---------------------------------------------------------------------------
class SubTaskSerializer(serializers.ModelSerializer):
    """Полное отображение подзадачи (используется для чтения и вложения)."""

    class Meta:
        model = SubTask
        fields = ("id", "title", "description", "task", "status", "deadline", "created_at")
        read_only_fields = ("id", "created_at")


# Задание 1. Переопределение поля: created_at только для чтения
class SubTaskCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = ("id", "title", "description", "task", "status", "deadline", "created_at")
        read_only_fields = ("id",)


# ---------------------------------------------------------------------------
# Задание 2. Категории: проверка уникальности названия в create и update
# ---------------------------------------------------------------------------
class CategoryCreateSerializer(serializers.ModelSerializer):
    # Поле объявлено явно, чтобы DRF не добавлял свой UniqueValidator:
    # уникальность проверяем сами в create() и update().
    name = serializers.CharField(max_length=100)

    class Meta:
        model = Category
        fields = ("id", "name")
        validators = []

    @staticmethod
    def _check_unique_name(name, exclude_pk=None):
        """Ошибка, если категория с таким названием уже есть (без учёта регистра).

        Сравниваем в Python через casefold(): SQLite не умеет сравнивать
        кириллицу без учёта регистра, а так проверка одинакова для любой БД.
        """
        names = Category.objects.exclude(pk=exclude_pk).values_list("name", flat=True)
        if any(existing.casefold() == name.strip().casefold() for existing in names):
            raise serializers.ValidationError(
                {"name": [f"Категория с названием «{name}» уже существует."]}
            )

    def create(self, validated_data):
        self._check_unique_name(validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get("name", instance.name)
        self._check_unique_name(name, exclude_pk=instance.pk)
        return super().update(instance, validated_data)


# ---------------------------------------------------------------------------
# Задачи
# ---------------------------------------------------------------------------
class TaskSerializer(serializers.ModelSerializer):
    """Краткое отображение задачи (для списка)."""

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "deadline", "created_at")
        read_only_fields = ("id", "created_at")


# Задание 3. Вложенный сериализатор: задача со всеми своими подзадачами
class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)  # related_name="subtasks"

    class Meta:
        model = Task
        fields = (
            "id", "title", "description", "categories",
            "status", "deadline", "created_at", "subtasks",
        )
        read_only_fields = ("id", "created_at")


# Задание 4. Валидация: дедлайн не может быть в прошлом
class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "categories", "status", "deadline", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом.")
        return value
