from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Читать объект может любой авторизованный пользователь,
    а изменять и удалять - только его владелец (автор)."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
