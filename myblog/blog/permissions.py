from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission. Only owners of objects can edit/delete.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are read-only, allow for any request.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
