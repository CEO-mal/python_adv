from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    SubTaskListCreateView,
    SubTaskRetrieveUpdateDestroyView,
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    TaskStatsView,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    # Задачи
    path("tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/stats/", TaskStatsView.as_view(), name="task-stats"),
    path("tasks/<int:pk>/", TaskRetrieveUpdateDestroyView.as_view(), name="task-detail"),
    # Подзадачи
    path("subtasks/", SubTaskListCreateView.as_view(), name="subtask-list-create"),
    path("subtasks/<int:pk>/", SubTaskRetrieveUpdateDestroyView.as_view(), name="subtask-detail"),
    # Категории (CRUD через ModelViewSet)
    path("", include(router.urls)),
]
