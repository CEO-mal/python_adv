from rest_framework.pagination import PageNumberPagination


class SubTaskPagination(PageNumberPagination):
    """Пагинация подзадач: не более 5 объектов на странице (?page=2, ?page=3 ...)."""

    page_size = 5
