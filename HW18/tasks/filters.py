import django_filters

from .models import STATUS_CHOICES, SubTask, Task


class TaskFilter(django_filters.FilterSet):
    """
    Фильтрация задач по status и deadline:
        ?status=done
        ?deadline=2026-12-31T18:00:00+01:00   — точное совпадение
        ?deadline_date=2026-12-31             — дедлайн в этот день
        ?deadline_after=2026-11-10            — дедлайн с этой даты (включительно)
        ?deadline_before=2026-11-30           — дедлайн по эту дату (включительно)
    """

    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)
    deadline = django_filters.IsoDateTimeFilter()
    deadline_date = django_filters.DateFilter(field_name="deadline", lookup_expr="date")
    deadline_after = django_filters.DateFilter(field_name="deadline", lookup_expr="date__gte")
    deadline_before = django_filters.DateFilter(field_name="deadline", lookup_expr="date__lte")

    class Meta:
        model = Task
        fields = ("status", "deadline")


class SubTaskFilter(TaskFilter):
    """Те же фильтры для подзадач + название главной задачи (?task_title=релиз)."""

    task_title = django_filters.CharFilter(field_name="task__title", lookup_expr="icontains")

    class Meta:
        model = SubTask
        fields = ("status", "deadline", "task_title")
