from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    SubTaskDetailUpdateDeleteView,
    SubTaskListCreateView,
    TaskCreateView,
    TaskDetailView,
    TaskListView,
    TaskStatsView,
)

urlpatterns = [
    # Задачи
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/stats/", TaskStatsView.as_view(), name="task-stats"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    # Подзадачи (APIView)
    path("subtasks/", SubTaskListCreateView.as_view(), name="subtask-list-create"),
    path(
        "subtasks/<int:pk>/",
        SubTaskDetailUpdateDeleteView.as_view(),
        name="subtask-detail-update-delete",
    ),
    # Категории
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
]
