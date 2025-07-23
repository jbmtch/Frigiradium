import factory
from faker import Faker
from django.contrib.auth.models import User, Household
from factory.django import DjangoModelFactory

class HouseholdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Household
    
    name = factory.Faker("last_name")

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall("set_password", "pass123")
    household = factory.SubFactory(HouseholdFactory)




    