import factory
from django.contrib.auth.models import User
from backend.inventory import models
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    password = factory.PostGenerationMethodCall("set_password", "pass123")

class HouseholdFactory(DjangoModelFactory):
    class Meta:
        model = models.Household

    name = factory.Faker("last_name")
    user = factory.SubFactory(UserFactory)

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

class UserInventoryFactory(DjangoModelFactory):
    class Meta:
        model = models.UserInventory

    user = factory.SubFactory(UserFactory)
    inventory = factory.SubFactory(InventoryFactory)

class MeasurementUnitFactory(DjangoModelFactory):
    class Meta: 
        model = models.MeasurementUnit

    # using only grams until i fully implement unit conversion
    name = "Grams"
    abbreviation = factory.Sequence(lambda n: f"g{n}")

class FoodItemFactory(DjangoModelFactory):
    class Meta:
        model = models.FoodItem

    name = factory.Faker('name')
    category = factory.Faker("random_element", elements=models.FoodCategory.values)
    user = factory.SubFactory(UserFactory)
    inventory = factory.SubFactory(InventoryFactory)
    storage_type = factory.Faker("random_element", elements=models.StorageType.values)
    expiration_date = factory.Faker('date_time_this_century', tzinfo=None)
    date_opened = factory.Faker('date_time_this_century', tzinfo=None)
    date_frozen = factory.Faker('date_time_this_century', tzinfo=None)
    date_purchased = factory.Faker('date_time_this_century', tzinfo=None)
    date_refridgerated = factory.Faker('date_time_this_century', tzinfo=None)
    isMeal = factory.Faker('boolean')
    amount = factory.Faker('randomize_nb_elements', number=200, max=250)
    unit = factory.SubFactory(MeasurementUnitFactory)



    

