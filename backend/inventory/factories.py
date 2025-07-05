import factory
from faker import Faker
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall("set_password", "pass123")

