import factory
from django.contrib.auth.models import User
from backend.inventory import models
from factory.django import DjangoModelFactory

class HouseholdFactory(DjangoModelFactory):
    class Meta:
        model = models.Household

    name = factory.Faker("last_name")

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    password = factory.PostGenerationMethodCall("set_password", "pass123")


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = models.UserProfile

    user = factory.SubFactory(UserFactory)
    household = factory.SubFactory(HouseholdFactory)

class InventoryFactory(DjangoModelFactory):
    class Meta:
        model = models.Inventory

    name = factory.Faker('last_name')
    household = factory.SubFactory(HouseholdFactory)
    

