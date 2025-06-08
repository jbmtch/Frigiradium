from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=5)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    household = models.ForeignKey(Household, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    phone_number = models.CharField(max_length=10)
    updated_at = models.DateTimeField(auto_now=True)



class Household(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)