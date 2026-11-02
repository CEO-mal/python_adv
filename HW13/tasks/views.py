from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import STATUS_CHOICES, Category, SubTask, Task
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


class TaskListView(generics.ListAPIView):
    """GET /api/tasks/ — список задач."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer


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

    def get(self, request):
        subtasks = SubTask.objects.all()
        serializer = SubTaskSerializer(subtasks, many=True)
        return Response(serializer.data)

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
