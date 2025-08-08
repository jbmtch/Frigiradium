import factory
from faker import Faker
from django.contrib.auth.models import User
from inventory.models import Household, UserProfile
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
    
# class UserFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = User

#     username = factory.Faker("user_name")
#     password = factory.PostGenerationMethodCall("set_password", "pass123")

#     @factory.post_generation
#     def create_profile(self, create, extracted, **kwargs):
#         if not create:
#             return
        
#         # if household was passed in, use it; else None
#         household = kwargs.pop("household", None)
#         profile, _ = UserProfile.objects.get_or_create(user=self)

#         if household: 
#             profile.household = household
#             profile.save()

class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    household = factory.SubFactory(HouseholdFactory)




    