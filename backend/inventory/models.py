from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=5)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    household = models.ForeignKey('Household', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    phone_number = models.CharField(max_length=10)
    updated_at = models.DateTimeField(auto_now=True)

class Household(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Inventory(models.Model):
    household = models.ForeignKey('Household', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FoodCategory(models.TextChoices):
    FRUIT = "FRUIT", "Fruit"
    VEGETABLE = "VEGETABLE", "Vegetable"
    GRAIN = "GRAIN", "Grain"
    DAIRY = "DAIRY", "Dairy"
    PROTEIN = "PROTEIN", "Protein"
    OTHER = "OTHER", "Other"

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=16, choices=FoodCategory.choices, default=FoodCategory.OTHER)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    inventory_id = models.ForeignKey('Inventory', on_delete=models.CASCADE)
    storage_type = models.CharField(max_length=50)
    expiration_date = models.DateTimeField()
    date_opened = models.DateTimeField(blank=True, null=True)
    date_frozen = models.DateTimeField(blank=True, null=True)
    date_purchased = models.DateTimeField()
    isMeal = models.BooleanField()
    date_refridgerated = models.DateTimeField(blank=True, null=True)
    amount = models.PositiveIntegerField(blank=True, null=True)
    unit = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



