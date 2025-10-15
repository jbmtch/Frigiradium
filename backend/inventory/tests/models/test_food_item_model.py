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


