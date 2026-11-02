from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    SubTaskListCreateView,
    SubTaskRetrieveUpdateDestroyView,
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    TaskStatsView,
)

urlpatterns = [
    # Задачи
    path("tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/stats/", TaskStatsView.as_view(), name="task-stats"),
    path("tasks/<int:pk>/", TaskRetrieveUpdateDestroyView.as_view(), name="task-detail"),
    # Подзадачи
    path("subtasks/", SubTaskListCreateView.as_view(), name="subtask-list-create"),
    path("subtasks/<int:pk>/", SubTaskRetrieveUpdateDestroyView.as_view(), name="subtask-detail"),
    # Категории
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
]
