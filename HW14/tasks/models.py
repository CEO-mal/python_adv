from django.db import models

STATUS_CHOICES = [
    ("new", "New"),
    ("in_progress", "In progress"),
    ("pending", "Pending"),
    ("blocked", "Blocked"),
    ("done", "Done"),
]


class Category(models.Model):
    """Категория выполнения."""

    name = models.CharField("Название категории", max_length=100)

    class Meta:
        db_table = "task_manager_category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_category_name"),
        ]

    def __str__(self):
        return self.name


class Task(models.Model):
    """Задача для выполнения."""

    title = models.CharField("Название задачи", max_length=200)
    description = models.TextField("Описание задачи", blank=True)
    categories = models.ManyToManyField(
        Category, related_name="tasks", blank=True, verbose_name="Категории"
    )
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="new")
    deadline = models.DateTimeField("Дедлайн")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        db_table = "task_manager_task"
        ordering = ["-created_at"]  # сначала новые
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        constraints = [
            models.UniqueConstraint(fields=["title"], name="unique_task_title"),
        ]

    def __str__(self):
        return self.title


class SubTask(models.Model):
    """Отдельная часть основной задачи (Task)."""

    title = models.CharField("Название подзадачи", max_length=200)
    description = models.TextField("Описание подзадачи", blank=True)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="subtasks", verbose_name="Основная задача"
    )
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="new")
    deadline = models.DateTimeField("Дедлайн")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        db_table = "task_manager_subtask"
        ordering = ["-created_at"]  # сначала новые
        verbose_name = "SubTask"
        verbose_name_plural = "SubTasks"
        constraints = [
            models.UniqueConstraint(fields=["title"], name="unique_subtask_title"),
        ]

    def __str__(self):
        return self.title
