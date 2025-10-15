import pytest
import random
import string
from django.core.exceptions import ValidationError
from inventory.tests.factories import factories

@pytest.mark.django_db
def test_name_length_validation():
    food_item = factories.FoodItemFactory()
    user = factories.UserFactory()
    inventory = factories.InventoryFactory()
    unit = factories.MeasurementUnitFactory()

    food_item.user = user
    food_item.inventory = inventory
    food_item.unit = unit


    too_long_name = "".join(
        random.choices(string.ascii_letters + string.digits, k=101)
    )
    food_item.name = too_long_name

    with pytest.raises(ValidationError) as excinfo:
        food_item.full_clean()

    assert "Ensure this value has at most 100 characters (it has 101)." in excinfo.value.message_dict["name"]

@pytest.mark.django_db
def test_name_not_blank():
    food_item = factories.FoodItemFactory.build(name='')
    user = factories.UserFactory()
    inventory = factories.InventoryFactory()
    unit = factories.MeasurementUnitFactory()

    food_item.user = user
    food_item.inventory = inventory
    food_item.unit = unit
    

    with pytest.raises(ValidationError) as excinfo:
        food_item.full_clean()

    assert excinfo.value.message_dict['name'] == ['This field cannot be blank.']

@pytest.mark.django_db
def test_category_only_valid_choices():
    food_item = factories.FoodItemFactory()
    user = factories.UserFactory()
    inventory = factories.InventoryFactory()
    unit = factories.MeasurementUnitFactory()

    food_item.user = user
    food_item.inventory = inventory
    food_item.unit = unit

    choices = ['FRUIT', 'VEGETABLE', 'GRAIN', 'DAIRY', 'PROTEIN' , 'OTHER']

    assert food_item.category in choices

@pytest.mark.django_db
def test_category_prevents_invalid_choices():
    food_item = factories.FoodItemFactory.build(category="SNACK")
    user = factories.UserFactory()
    inventory = factories.InventoryFactory()
    unit = factories.MeasurementUnitFactory()

    food_item.user = user
    food_item.inventory = inventory
    food_item.unit = unit

    choices = ['FRUIT', 'VEGETABLE', 'GRAIN', 'DAIRY', 'PROTEIN' , 'OTHER']

    with pytest.raises(ValidationError) as excinfo:
        food_item.full_clean()

    assert food_item.category not in choices
    assert excinfo.value.message_dict['category'] == ["Value 'SNACK' is not a valid choice."]

@pytest.mark.django_db
def test_storage_type_only_valid_choices():
    food_item = factories.FoodItemFactory()
    user = factories.UserFactory()
    inventory = factories.InventoryFactory()
    unit = factories.MeasurementUnitFactory()

    food_item.user = user
    food_item.inventory = inventory
    food_item.unit = unit

    choices = ['FRIDGE', 'FREEZER', 'PANTRY', 'COUNTER']

    assert food_item.storage_type in choices

@pytest.mark.django_db
def test_storage_type_prevents_invalid_choices():
    food_item = factories.FoodItemFactory.build(storage_type="TABLE")
    user = factories.UserFactory()
    inventory = factories.InventoryFactory()
    unit = factories.MeasurementUnitFactory()

    food_item.user = user
    food_item.inventory = inventory
    food_item.unit = unit

    choices = ['FRIDGE', 'FREEZER', 'PANTRY', 'COUNTER']

    with pytest.raises(ValidationError) as excinfo:
        food_item.full_clean()

    assert food_item.storage_type not in choices
    assert excinfo.value.message_dict['storage_type'] == ["Value 'TABLE' is not a valid choice."]

