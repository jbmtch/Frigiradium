from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from inventory.serializers import UserProfileSerializer, HouseholdSerializer, InventorySerializer, UserInventorySerializer
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from inventory.models import UserProfile, Household, Inventory, UserInventory
from inventory.permissions import IsHouseholdOwner

# Create your views here.

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()

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
        # only should be able to see your own inventory
        return Inventory.objects.filter(memberships__user=user).distinct()
    
    def perform_create(self, serializer):
        household_id = self.kwargs.get("household_id")
        household = get_object_or_404(Household, pk=household_id)
        
        if not household.members.filter(user=self.request.user).exists():
            raise PermissionDenied("You must already be a member of this household to create an inventory within this household.")
        inventory = serializer.save()
        UserInventory.objects.create(user=self.request.user, inventory=inventory)

    def perform_update(self, serializer):
        serializer.save()

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
        # Only users who already belong to an inventory can manage memberships for it
        if not inventory.memberships.filter(user=self.request.user).exists():
            raise PermissionDenied("You must already be a member of this inventory to add members.")
        serializer.save()

    def perform_update(self, serializer):
        inventory = serializer.validated_data.get('inventory', serializer.instance.inventory)
        # `partial=True` on PATCH requests means the incoming payload may omit the
        # inventory field. `validated_data` only contains keys provided by the
        # client, so we fall back to the current instance's inventory when it is
        # absent. This preserves the permission check while avoiding a KeyError
        # on partial updates.
        if not inventory.memberships.filter(user=self.request.user).exists():
            raise PermissionDenied("You must already be a member of this inventory to perform updates.")
        serializer.save()
