from rest_framework import permissions

class IsReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow safe methods (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
