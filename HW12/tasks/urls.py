from django.urls import path

from .views import TaskCreateView, TaskDetailView, TaskListView, TaskStatsView

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="task-list"),             # GET  — список задач
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),  # POST — создание задачи
    path("tasks/stats/", TaskStatsView.as_view(), name="task-stats"),     # GET  — статистика
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),  # GET — задача по ID
]
