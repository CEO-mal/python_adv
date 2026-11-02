from django.db.models import Count
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import STATUS_CHOICES, Task
from .serializers import TaskSerializer


# ---------------------------------------------------------------------------
# Задание 1. Создание задачи
# POST /api/tasks/create/
# ---------------------------------------------------------------------------
class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


# ---------------------------------------------------------------------------
# Задание 2. Список задач и задача по ID
# GET /api/tasks/
# GET /api/tasks/<id>/
# ---------------------------------------------------------------------------
class TaskListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer  # несуществующий ID -> 404 Not Found


# ---------------------------------------------------------------------------
# Задание 3. Статистика задач
# GET /api/tasks/stats/
# ---------------------------------------------------------------------------
class TaskStatsView(APIView):
    def get(self, request):
        total = Task.objects.count()

        # Количество задач по каждому статусу (одним запросом с GROUP BY)
        counts = dict(
            Task.objects.values_list("status").annotate(count=Count("id")).order_by()
        )
        by_status = {code: counts.get(code, 0) for code, _ in STATUS_CHOICES}

        # Просроченные: дедлайн прошёл, а задача ещё не выполнена
        overdue = (
            Task.objects.filter(deadline__lt=timezone.now()).exclude(status="done").count()
        )

        return Response(
            {
                "total_tasks": total,
                "by_status": by_status,
                "overdue_tasks": overdue,
            }
        )
