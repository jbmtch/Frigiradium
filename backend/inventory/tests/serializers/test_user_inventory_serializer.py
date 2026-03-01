import pytest

from inventory.serializers import UserInventorySerializer
from inventory.tests.factories import factories


@pytest.mark.django_db
def test_validate_returns_attrs_for_valid_membership():
    household = factories.HouseholdFactory()
    user = factories.UserFactory()
    inventory = factories.InventoryFactory(household=household)

    user.userprofile.household = household
    user.userprofile.save(update_fields=["household"])

    serializer = UserInventorySerializer(data={"user": user.id, "inventory": inventory.id})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["user"] == user
    assert serializer.validated_data["inventory"] == inventory


@pytest.mark.django_db
def test_validate_rejects_user_not_in_household():
    household = factories.HouseholdFactory()
    outsider = factories.UserFactory()
    inventory = factories.InventoryFactory(household=household)

    serializer = UserInventorySerializer(data={"user": outsider.id, "inventory": inventory.id})

    assert not serializer.is_valid()
    assert serializer.errors["non_field_errors"] == [
        "User must belong to the inventory's household to be added."
    ]


@pytest.mark.django_db
def test_validate_rejects_inventory_without_household():
    user = factories.UserFactory()
    inventory = factories.InventoryFactory(household=None)

    serializer = UserInventorySerializer(data={"user": user.id, "inventory": inventory.id})

    assert not serializer.is_valid()
    assert serializer.errors["non_field_errors"] == ["Inventories must belong to a household."]
