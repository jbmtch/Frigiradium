from django.shortcuts import render
from django.db.models import Q
from inventory.serializers import UserProfileSerializer, HouseholdSerializer, InventorySerializer, UserInventorySerializer
from rest_framework import permissions, viewsets
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
        inventory = serializer.save()
        UserInventory.objects.create(user=self.request.user, inventory=inventory)

    def perform_update(self, serializer):
        serializer.save()

class UserInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserInventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserInventory.objects.all()

    def get_queryset(self):
        user = self.request.user
        # Show only memberships that involve inventories the user belongs to
        return UserInventory.objects.filter(user=user)
