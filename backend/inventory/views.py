from django.shortcuts import render
from django.db.models import Q
from inventory.serializers import UserProfileSerializer, HouseholdSerializer
from rest_framework import permissions, viewsets
from inventory.models import UserProfile, Household
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
