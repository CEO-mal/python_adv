from rest_framework.pagination import CursorPagination, PageNumberPagination


class SubTaskPagination(PageNumberPagination):
    """Пагинация подзадач: не более 5 объектов на странице (?page=2, ?page=3 ...)."""

    page_size = 5


class SafeCursorPagination(CursorPagination):
    """HW17. Глобальная курсорная пагинация: в адресе только зашифрованный курсор.

    Номер страницы, смещение и размер выборки не видны клиенту,
    а размер страницы задаётся только на сервере (не более 6 объектов).
    """

    page_size = 6
    ordering = "-id"  # поле сортировки есть у любой модели
