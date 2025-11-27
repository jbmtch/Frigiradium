from django.shortcuts import render
from inventory.serializers import UserProfileSerializer, HouseholdSerializer
from rest_framework import permissions, viewsets
from inventory.models import UserProfile, Household
# Create your views here.

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()

class HouseholdViewSet(viewsets.ModelViewSet):
    serializer_class = HouseholdSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Household.objects.all()

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
