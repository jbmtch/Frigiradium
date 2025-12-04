import random
import string

import pytest
from django.core.exceptions import ValidationError


from inventory.tests.factories import factories


@pytest.mark.django_db
def test_inventory_assigned_to_household():
    inventory = factories.InventoryFactory()
    household = factories.HouseholdFactory(name="Test Household")

    inventory.household = household
    inventory.save()

    assert inventory.household is not None
    assert inventory.household.name == "Test Household"
    assert household.id == inventory.household.id


@pytest.mark.django_db
def test_inventory_timestamp_updates_after_edits():
    inventory = factories.InventoryFactory()

    first_update_time = inventory.updated_at
    initial_creation_time = inventory.created_at

    inventory.name = "New Last Name"
    inventory.save()

    assert initial_creation_time == inventory.created_at
    assert first_update_time < inventory.updated_at


@pytest.mark.django_db
def test_inventory_household_set_to_null_upon_household_deletion():
    inventory = factories.InventoryFactory()
    household = factories.HouseholdFactory()

    inventory.household = household
    inventory.save()

    assert inventory.household is not None
    assert household.id == inventory.household.id

    inventory.household.delete()
    inventory.refresh_from_db()

    assert inventory.household is None


@pytest.mark.django_db
def test_inventory_name_length_constraint():
    inventory = factories.InventoryFactory()

    too_long_string = "".join(
        random.choices(string.ascii_letters + string.digits, k=101)
    )
    inventory.name = too_long_string

    with pytest.raises(ValidationError) as excinfo:
        inventory.full_clean()

    assert "Ensure this value has at most 100 characters (it has 101)." in excinfo.value.message_dict["name"]

@pytest.mark.django_db
def test_inventory_name_not_blank():
    inventory = factories.InventoryFactory.build(name='')

    with pytest.raises(ValidationError) as excinfo:
        inventory.full_clean()

    assert excinfo.value.message_dict['name'] == ["This field cannot be blank."]

@pytest.mark.django_db
def test_inventory_can_exist_without_household():
    inventory = factories.InventoryFactory.build(household=None)

    inventory.full_clean()

    inventory.save()
    inventory.refresh_from_db()

    assert inventory.household is None

@pytest.mark.django_db
def test_user_can_belong_to_multiple_inventories():
    user = factories.UserFactory()
    household = factories.HouseholdFactory()
    inv1 = factories.InventoryFactory.create(household=household)
    inv2 = factories.InventoryFactory.create(household=household)

    factories.UserInventoryFactory.create(user=user, inventory=inv1)
    factories.UserInventoryFactory.create(user=user, inventory=inv2)

    inventories = user.inventories.all()

    assert inventories.count() == 2
    assert {inv1.id, inv2.id} == set(inventories.values_list("id", flat=True))

@pytest.mark.django_db
def test_inventory_can_have_multiple_users():
    user1 = factories.UserFactory()
    user2 = factories.UserFactory()
    household = factories.HouseholdFactory()
    inv = factories.InventoryFactory(household=household)

    factories.UserInventoryFactory.create(user=user1, inventory=inv)
    factories.UserInventoryFactory.create(user=user2, inventory=inv)

    users = inv.memberships.all()

    assert users.count() == 2
    assert {users[0].user.id, users[1].user.id} == set(users.values_list("id", flat=True))

    