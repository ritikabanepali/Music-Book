# albums/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    Assumes the model instance has a `user` attribute.
    """

    def has_permission(self, request, view): # for logged in users
        # Read permissions allowed for any request,
        # write permissions require authentication.
        if request.method in permissions.SAFE_METHODS: # read
            return True
        return request.user and request.user.is_authenticated # CUD

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed for any request,
        # write permissions only for the owner.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
