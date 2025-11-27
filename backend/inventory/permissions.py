from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsHouseholdOwner(BasePermission):
    """Allow only household owners to modify the object.

    Members can still perform safe (read-only) requests, but write operations
    require ownership.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.user == request.user or obj.members.filter(user=request.user).exists()
        
        return obj.user == request.user