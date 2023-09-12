from rest_framework import permissions

# Проверяем, является ли пользователь владельцем аккаунта.
class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and view.kwargs.get('pk') == str(request.user.pk)

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user == request.user

