from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

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


# ===========================================================================
# Задачи
# ===========================================================================
class TaskCreateView(generics.CreateAPIView):
    """POST /api/tasks/create/ — создание задачи (дедлайн не в прошлом)."""

    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer


# Задание 1. Дни недели -> номер дня по ISO (понедельник = 1 ... воскресенье = 7)
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


class TaskListView(generics.ListAPIView):
    """
    GET /api/tasks/                    — все задачи
    GET /api/tasks/?weekday=вторник    — задачи с дедлайном во вторник
    (также: ?weekday=tuesday, ?weekday=вт, ?weekday=2)
    """

    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        weekday = self.request.query_params.get("weekday")
        if not weekday:  # параметр не передан -> все задачи
            return queryset

        value = weekday.strip().casefold()
        day = int(value) if value.isdigit() else WEEKDAY_BY_NAME.get(value)
        if day not in WEEKDAYS:
            raise ValidationError(
                {"weekday": [f"Неизвестный день недели «{weekday}». "
                             "Пример: понедельник, вторник ... воскресенье (или 1–7)."]}
            )
        # День недели считается по дедлайну, в часовом поясе проекта (TIME_ZONE)
        return queryset.filter(deadline__iso_week_day=day)


class TaskDetailView(generics.RetrieveAPIView):
    """GET /api/tasks/<id>/ — задача со всеми подзадачами."""

    queryset = Task.objects.prefetch_related("subtasks")
    serializer_class = TaskDetailSerializer


class TaskStatsView(APIView):
    """GET /api/tasks/stats/ — статистика задач."""

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
# Задание 5. Подзадачи на APIView
# ===========================================================================
class SubTaskListCreateView(APIView):
    """
    GET  /api/subtasks/ — список подзадач
    POST /api/subtasks/ — создание подзадачи
    """

    """
    Задание 2: пагинация по 5 объектов, сначала самые новые.
    Задание 3: фильтры (можно по отдельности или вместе):
        ?task_title=<название главной задачи>
        ?status=<new | in_progress | pending | blocked | done>
    Пример: /api/subtasks/?task_title=Релиз&status=done&page=2
    """

    pagination_class = SubTaskPagination

    def get(self, request):
        subtasks = SubTask.objects.select_related("task").order_by("-created_at", "-id")

        task_title = request.query_params.get("task_title")
        if task_title:
            subtasks = subtasks.filter(task__title__icontains=task_title.strip())

        status_param = request.query_params.get("status")
        if status_param:
            allowed = [code for code, _ in STATUS_CHOICES]
            if status_param not in allowed:
                raise ValidationError(
                    {"status": [f"Неизвестный статус «{status_param}». Доступны: {', '.join(allowed)}."]}
                )
            subtasks = subtasks.filter(status=status_param)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subtasks, request, view=self)
        serializer = SubTaskSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # ошибки -> 400 Bad Request
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubTaskDetailUpdateDeleteView(APIView):
    """
    GET    /api/subtasks/<id>/ — получить подзадачу
    PUT    /api/subtasks/<id>/ — полностью обновить
    PATCH  /api/subtasks/<id>/ — частично обновить
    DELETE /api/subtasks/<id>/ — удалить
    """

    def get_object(self, pk):
        return get_object_or_404(SubTask, pk=pk)  # нет такой -> 404 Not Found

    def get(self, request, pk):
        serializer = SubTaskSerializer(self.get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk):
        serializer = SubTaskCreateSerializer(self.get_object(pk), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        serializer = SubTaskCreateSerializer(
            self.get_object(pk), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===========================================================================
# Категории (чтобы проверить CategoryCreateSerializer из задания 2)
# ===========================================================================
class CategoryListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/categories/"""

    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/categories/<id>/"""

    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
