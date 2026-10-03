from datetime import timedelta

from django.utils import timezone

from tasks.models import SubTask, Task

now = timezone.now()

# ---------- 1. Создание записей ----------
task = Task.objects.create(
    title="Prepare presentation",
    description="Prepare materials and slides for the presentation",
    status="new",
    deadline=now + timedelta(days=3),
)
SubTask.objects.create(
    title="Gather information",
    description="Find necessary information for the presentation",
    status="new",
    deadline=now + timedelta(days=2),
    task=task,
)
SubTask.objects.create(
    title="Create slides",
    description="Create presentation slides",
    status="new",
    deadline=now + timedelta(days=1),
    task=task,
)
print("Создано:", task, list(task.subtasks.all()))

# ---------- 2. Чтение записей ----------
new_tasks = Task.objects.filter(status="new")
print("Tasks со статусом New:", list(new_tasks))

overdue_done = SubTask.objects.filter(status="done", deadline__lt=timezone.now())
print("SubTasks Done с истёкшим сроком:", list(overdue_done))

# ---------- 3. Изменение записей ----------
Task.objects.filter(title="Prepare presentation").update(status="in_progress")
SubTask.objects.filter(title="Gather information").update(
    deadline=timezone.now() - timedelta(days=2)
)
SubTask.objects.filter(title="Create slides").update(
    description="Create and format presentation slides"
)

task = Task.objects.get(title="Prepare presentation")
print("Статус задачи:", task.get_status_display())
print("Дедлайн Gather information:", SubTask.objects.get(title="Gather information").deadline)
print("Описание Create slides:", SubTask.objects.get(title="Create slides").description)

# ---------- 4. Удаление записей ----------
# Подзадачи удаляются вместе с задачей (on_delete=models.CASCADE)
deleted = Task.objects.filter(title="Prepare presentation").delete()
print("Удалено:", deleted)
print("Осталось подзадач задачи:", SubTask.objects.filter(task__title="Prepare presentation").count())
