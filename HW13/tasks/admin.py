from django.contrib import admin, messages

from .models import Category, SubTask, Task


# ---------------------------------------------------------------------------
# Задание 1. Инлайн-форма: подзадачу можно создать сразу при создании задачи
# ---------------------------------------------------------------------------
class SubTaskInline(admin.TabularInline):
    """Подзадачи прямо на странице задачи."""

    model = SubTask
    extra = 1  # одна пустая форма подзадачи при создании задачи
    fields = ("title", "description", "status", "deadline")
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "tasks_count")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)

    @admin.display(description="Кол-во задач")
    def tasks_count(self, obj):
        return obj.tasks.count()


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # Задание 2: в списке задач — укороченное название (short_title)
    list_display = ("id", "short_title", "status", "category_list", "deadline", "created_at")
    list_display_links = ("id", "short_title")
    list_editable = ("status",)  # статус можно менять прямо в списке
    list_filter = ("status", "categories", "deadline", "created_at")
    search_fields = ("title", "description")
    date_hierarchy = "deadline"
    filter_horizontal = ("categories",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("title", "description")}),
        ("Параметры", {"fields": ("categories", "status", "deadline", "created_at")}),
    )
    inlines = [SubTaskInline]
    list_per_page = 20

    @admin.display(description="Название задачи", ordering="title")
    def short_title(self, obj):
        """Первые 10 символов названия + «...», если название длиннее.

        Task.__str__ по-прежнему возвращает полное название, поэтому
        при выборе задачи для подзадачи (ForeignKey / autocomplete)
        отображается полное название.
        """
        if len(obj.title) > 10:
            return f"{obj.title[:10]}..."
        return obj.title

    @admin.display(description="Категории")
    def category_list(self, obj):
        return ", ".join(c.name for c in obj.categories.all()) or "—"


# ---------------------------------------------------------------------------
# Задание 3. Свой action: перевести выбранные подзадачи в статус Done
# ---------------------------------------------------------------------------
@admin.action(description="Перевести выбранные подзадачи в статус Done")
def mark_as_done(modeladmin, request, queryset):
    updated = queryset.update(status="done")
    modeladmin.message_user(
        request,
        f"Подзадач переведено в статус Done: {updated}",
        messages.SUCCESS,
    )


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "task", "status", "deadline", "created_at")
    list_display_links = ("id", "title")
    list_editable = ("status",)
    list_filter = ("status", "task", "deadline")
    search_fields = ("title", "description", "task__title")
    autocomplete_fields = ("task",)  # в выборе задачи — полное название (Task.__str__)
    readonly_fields = ("created_at",)
    list_per_page = 20
    actions = [mark_as_done]
