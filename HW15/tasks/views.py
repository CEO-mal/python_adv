from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import SubTaskFilter, TaskFilter
from .models import STATUS_CHOICES, Category, SubTask, Task
from .pagination import SubTaskPagination
from .serializers import (
    CategoryCreateSerializer,
    SubTaskCreateSerializer,
    SubTaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskSerializer,
)

# Общие настройки фильтрации, поиска и сортировки
FILTER_BACKENDS = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


# ===========================================================================
# Задание 1. Задачи (Tasks) на Generic Views
# ===========================================================================
WEEKDAYS = {
    1: ("понедельник", "пн", "monday", "mon"),
    2: ("вторник", "вт", "tuesday", "tue"),
    3: ("среда", "ср", "wednesday", "wed"),
    4: ("четверг", "чт", "thursday", "thu"),
    5: ("пятница", "пт", "friday", "fri"),
    6: ("суббота", "сб", "saturday", "sat"),
    7: ("воскресенье", "вс", "sunday", "sun"),
}
WEEKDAY_BY_NAME = {name: num for num, names in WEEKDAYS.items() for name in names}


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/ — список задач
    POST /api/tasks/ — создание задачи

    Фильтрация: ?status=new, ?deadline=..., ?deadline_date=2026-12-31,
                ?deadline_after=..., ?deadline_before=..., ?weekday=вторник
    Поиск:      ?search=<текст> (по title и description)
    Сортировка: ?ordering=created_at или ?ordering=-created_at (по умолчанию — новые сверху)
    """

    filter_backends = FILTER_BACKENDS
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskCreateSerializer  # с проверкой: дедлайн не в прошлом
        return TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        # Фильтр по дню недели из HW14 оставлен
        weekday = self.request.query_params.get("weekday")
        if weekday:
            value = weekday.strip().casefold()
            day = int(value) if value.isdigit() else WEEKDAY_BY_NAME.get(value)
            if day not in WEEKDAYS:
                raise ValidationError({"weekday": [f"Неизвестный день недели «{weekday}»."]})
            queryset = queryset.filter(deadline__iso_week_day=day)
        return queryset


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/<id>/ — задача со всеми подзадачами
    PUT    /api/tasks/<id>/ — полное обновление
    PATCH  /api/tasks/<id>/ — частичное обновление
    DELETE /api/tasks/<id>/ — удаление
    """

    queryset = Task.objects.prefetch_related("subtasks")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskDetailSerializer
        return TaskCreateSerializer


class TaskStatsView(APIView):
    """GET /api/tasks/stats/ — статистика задач (без изменений)."""

    def get(self, request):
        counts = dict(
            Task.objects.values_list("status").annotate(count=Count("id")).order_by()
        )
        return Response(
            {
                "total_tasks": Task.objects.count(),
                "by_status": {code: counts.get(code, 0) for code, _ in STATUS_CHOICES},
                "overdue_tasks": Task.objects.filter(deadline__lt=timezone.now())
                .exclude(status="done")
                .count(),
            }
        )


# ===========================================================================
# Задание 2. Подзадачи (SubTasks) на Generic Views
# ===========================================================================
class SubTaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/subtasks/ — список подзадач (по 5 на странице)
    POST /api/subtasks/ — создание подзадачи

    Фильтрация: ?status=done, ?deadline=..., ?deadline_date=..., ?task_title=релиз
    Поиск:      ?search=<текст> (по title и description)
    Сортировка: ?ordering=created_at или ?ordering=-created_at (по умолчанию — новые сверху)
    """

    queryset = SubTask.objects.select_related("task")
    pagination_class = SubTaskPagination
    filter_backends = FILTER_BACKENDS
    filterset_class = SubTaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at", "-id"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SubTaskCreateSerializer
        return SubTaskSerializer


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/subtasks/<id>/ — получить подзадачу
    PUT    /api/subtasks/<id>/ — полное обновление
    PATCH  /api/subtasks/<id>/ — частичное обновление
    DELETE /api/subtasks/<id>/ — удаление
    """

    queryset = SubTask.objects.select_related("task")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SubTaskSerializer
        return SubTaskCreateSerializer


# ===========================================================================
# Категории
# ===========================================================================
class CategoryListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/categories/"""

    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/categories/<id>/"""

    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
