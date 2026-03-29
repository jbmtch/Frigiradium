from django.shortcuts import get_object_or_404
from django.db.models import Q
from inventory.serializers import UserProfileSerializer, HouseholdSerializer, InventorySerializer, UserInventorySerializer, FoodItemSerializer
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from inventory.models import UserProfile, Household, Inventory, UserInventory, FoodItem
from inventory.permissions import IsHouseholdOwner, IsFoodItemOwnerOrVisibleInHousehold

# Create your views here.

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HouseholdViewSet(viewsets.ModelViewSet):
    serializer_class = HouseholdSerializer
    permission_classes = [permissions.IsAuthenticated, IsHouseholdOwner]
    queryset = Household.objects.all()

    def get_queryset(self):
        user = self.request.user
        # fetches households the user owns or is a member of.
        return super().get_queryset().filter(Q(user=user) | Q(members__user=user)).distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Inventory.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        # only should be able to see your own inventory, from households you belong to
        household_id = self.kwargs.get("household_id")
        queryset = Inventory.objects.filter(memberships__user=user).distinct()
        if household_id is not None:
            queryset = queryset.filter(household_id=household_id)
        return queryset
    
    def perform_create(self, serializer):
        household_id = self.kwargs.get("household_id")
        if household_id is None:
            raise ValidationError({"household": ["Use the household inventory endpoint to create an inventory."]})
        household = get_object_or_404(Household, pk=household_id)

        if not (household.user == self.request.user or household.members.filter(user=self.request.user).exists()):
            raise PermissionDenied("You must be a member of this household to create an inventory within it.")

        inventory = serializer.save(household=household)
        UserInventory.objects.create(user=self.request.user, inventory=inventory)

    def perform_update(self, serializer):
        household_id = serializer.instance.household.id
        household = get_object_or_404(Household, pk=household_id)

        if not (household.user == self.request.user or household.members.filter(user=self.request.user).exists()):
            raise PermissionDenied("You must be a member of this household to update an inventory within it.")
        serializer.save()

    def perform_destroy(self, instance):
        household = instance.household
        if household is None or household.user != self.request.user:
            raise PermissionDenied("Only the household owner can delete an inventory.")
        instance.delete()

class UserInventoryViewSet(viewsets.ModelViewSet):
    serializer_class = UserInventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserInventory.objects.all()

    def get_queryset(self):
        user = self.request.user
        # Show only memberships that involve inventories the user belongs to
        return UserInventory.objects.filter(inventory__memberships__user=user).distinct()
    
    def perform_create(self, serializer):
        inventory = serializer.validated_data['inventory']
        user = serializer.validated_data['user']
        # Only users who already belong to an inventory can manage memberships for it
        if not inventory.memberships.filter(user=self.request.user).exists():
            raise PermissionDenied("You must already be a member of this inventory to add members.")
        
        household = inventory.household
        if household is None:
            raise PermissionDenied("Inventories must belong to a household.")
        is_owner = household.user_id == user.id
        is_member = household.members.filter(user=user).exists()

        if not (is_owner or is_member):
            raise PermissionDenied("User must belong to this household to be added to the inventory.")
        serializer.save()

    def perform_update(self, serializer):
        requester = self.request.user
        membership = serializer.instance
        inventory = serializer.validated_data.get('inventory', membership.inventory)
        # `partial=True` on PATCH requests means the incoming payload may omit the
        # inventory field. `validated_data` only contains keys provided by the
        # client, so we fall back to the current instance's inventory when it is
        # absent. This preserves the permission check while avoiding a KeyError
        # on partial updates.
        if not inventory.memberships.filter(user=requester).exists():
            raise PermissionDenied("You must already be a member of this inventory to perform updates.")

        household = inventory.household
        is_self_update = membership.user_id == requester.id
        is_household_owner = household is not None and household.user_id == requester.id
        next_user = serializer.validated_data.get('user', membership.user)
        changing_assigned_user = next_user.id != membership.user_id

        if changing_assigned_user and not is_household_owner:
            raise PermissionDenied("Only the household owner can reassign inventory memberships.")

        if not (is_self_update or is_household_owner):
            raise PermissionDenied("Only the household owner can update other inventory memberships.")
        serializer.save()

    def perform_destroy(self, instance):
        inventory = instance.inventory
        household = inventory.household
        requester = self.request.user

        if not inventory.memberships.filter(user=requester).exists():
            raise PermissionDenied("You must already be a member of this inventory to remove members.")

        is_self_removal = instance.user_id == requester.id
        is_household_owner = household is not None and household.user_id == requester.id

        if not (is_self_removal or is_household_owner):
            raise PermissionDenied("Only the household owner can remove other inventory members.")

        if inventory.memberships.count() <= 1:
            raise PermissionDenied("An inventory must have at least one member.")

        instance.delete()


class FoodItemViewSet(viewsets.ModelViewSet):
    serializer_class = FoodItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsFoodItemOwnerOrVisibleInHousehold]
    queryset = FoodItem.objects.select_related("inventory", "inventory__household", "user", "unit")

    def _household_membership_filter(self, user):
        return Q(inventory__household__user=user) | Q(inventory__household__members__user=user)

    def get_queryset(self):
        user = self.request.user
        household_id = self.kwargs.get("household_id")
        inventory_id = self.kwargs.get("inventory_id")

        base = self.queryset
        if household_id is not None:
            base = base.filter(inventory__household_id=household_id)
        if inventory_id is not None:
            base = base.filter(inventory_id=inventory_id)

        own_items = Q(user=user, inventory__memberships__user=user)
        shared_items = Q(
            inventory__household__allow_member_item_visibility=True
        ) & self._household_membership_filter(user)

        return base.filter(own_items | shared_items).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        household_id = self.kwargs.get("household_id")
        inventory_id = self.kwargs.get("inventory_id")
        context["household_id"] = int(household_id) if household_id is not None else None
        context["inventory_id"] = int(inventory_id) if inventory_id is not None else None
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user.id:
            raise PermissionDenied("You can only update your own food items.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied("You can only delete your own food items.")
        instance.delete()
