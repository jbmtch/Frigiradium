from django.shortcuts import render
from inventory.serializers import UserProfileSerializer
from rest_framework import permissions, viewsets
from inventory.models import UserProfile
# Create your views here.

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()