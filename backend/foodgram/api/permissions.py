from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        result = []
        for group in request.user.groups.all():
            result.append(group.name)
        return(
            request.method in permissions.SAFE_METHODS 
            or request.user == obj.author
            or 'admin' in result)
        
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        result = []
        for group in request.user.groups.all():
            result.append(group.name)
        return 'admin' in result