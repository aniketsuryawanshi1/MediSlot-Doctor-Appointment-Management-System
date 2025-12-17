from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """Permission to allow only the owner or admin to access (e.g., for appointments)."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsAuthenticatedAndActive(BasePermission):
    """Permission to ensure user is authenticated and active."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active