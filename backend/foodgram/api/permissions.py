from rest_framework import permissions


class IsStaffAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        result = []
        for group in request.user.groups.all():
            result.append(group.name)
        return(
            request.method in permissions.SAFE_METHODS 
            or request.user == obj.author
            or 'admin' in result)