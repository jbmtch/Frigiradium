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


class IsFoodItemOwnerOrVisibleInHousehold(BasePermission):
    """Write access is item-owner only; reads can expand to household members.

    Household members can read another member's food item only when the
    household owner has explicitly enabled member item visibility.
    """

    def has_object_permission(self, request, view, obj):
        if obj.user_id == request.user.id:
            return True

        if request.method not in SAFE_METHODS:
            return False

        household = obj.inventory.household
        if household is None or not household.allow_member_item_visibility:
            return False

        return household.user_id == request.user.id or household.members.filter(user=request.user).exists()
