from django.contrib import admin

from .models import Category, SubTask, Task


class SubTaskInline(admin.TabularInline):
    """Подзадачи прямо на странице задачи."""

    model = SubTask
    extra = 1
    fields = ("title", "status", "deadline")


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
    list_display = ("id", "title", "status", "category_list", "deadline", "created_at")
    list_display_links = ("id", "title")
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

    @admin.display(description="Категории")
    def category_list(self, obj):
        return ", ".join(c.name for c in obj.categories.all()) or "—"


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "task", "status", "deadline", "created_at")
    list_display_links = ("id", "title")
    list_editable = ("status",)
    list_filter = ("status", "task", "deadline")
    search_fields = ("title", "description", "task__title")
    autocomplete_fields = ("task",)
    readonly_fields = ("created_at",)
    list_per_page = 20
