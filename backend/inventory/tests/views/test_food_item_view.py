import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from inventory.tests.factories import factories


def _food_item_payload(unit_id, inventory_id, name="Milk"):
    now = timezone.now().isoformat()
    return {
        "name": name,
        "category": "DAIRY",
        "inventory": inventory_id,
        "storage_type": "FRIDGE",
        "expiration_date": now,
        "date_opened": now,
        "date_frozen": now,
        "date_purchased": now,
        "isMeal": False,
        "date_refridgerated": now,
        "amount": 1,
        "unit": unit_id,
    }


@pytest.mark.django_db
def test_user_sees_own_inventory_items_only():
    client = APIClient()
    user = factories.UserFactory()
    other_user = factories.UserFactory()
    household = factories.HouseholdFactory(user=user)
    user.userprofile.household = household
    user.userprofile.save(update_fields=["household"])
    other_user.userprofile.household = household
    other_user.userprofile.save(update_fields=["household"])

    own_inventory = factories.InventoryFactory(household=household)
    other_inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=user, inventory=own_inventory)
    factories.UserInventoryFactory(user=other_user, inventory=other_inventory)

    own_item = factories.FoodItemFactory(user=user, inventory=own_inventory)
    factories.FoodItemFactory(user=other_user, inventory=other_inventory)

    client.force_authenticate(user=user)
    response = client.get(reverse("food-item-list"))

    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert ids == [own_item.id]


@pytest.mark.django_db
def test_user_cannot_see_other_user_items_in_same_household_by_default():
    client = APIClient()
    owner = factories.UserFactory()
    member = factories.UserFactory()
    household = factories.HouseholdFactory(user=owner, allow_member_item_visibility=False)
    owner.userprofile.household = household
    owner.userprofile.save(update_fields=["household"])
    member.userprofile.household = household
    member.userprofile.save(update_fields=["household"])

    owner_inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=owner, inventory=owner_inventory)
    item = factories.FoodItemFactory(user=owner, inventory=owner_inventory)

    client.force_authenticate(user=member)
    response = client.get(reverse("food-item-detail", args=[item.id]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_cannot_see_other_user_items_in_different_household():
    client = APIClient()
    user = factories.UserFactory()
    other_owner = factories.UserFactory()
    my_household = factories.HouseholdFactory(user=user)
    other_household = factories.HouseholdFactory(user=other_owner, allow_member_item_visibility=True)

    user.userprofile.household = my_household
    user.userprofile.save(update_fields=["household"])

    other_inventory = factories.InventoryFactory(household=other_household)
    factories.UserInventoryFactory(user=other_owner, inventory=other_inventory)
    other_item = factories.FoodItemFactory(user=other_owner, inventory=other_inventory)

    client.force_authenticate(user=user)
    response = client.get(reverse("food-item-detail", args=[other_item.id]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_cannot_create_item_in_another_users_inventory():
    client = APIClient()
    user = factories.UserFactory()
    owner = factories.UserFactory()
    household = factories.HouseholdFactory(user=owner)
    user.userprofile.household = household
    user.userprofile.save(update_fields=["household"])

    owner_inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=owner, inventory=owner_inventory)
    unit = factories.MeasurementUnitFactory()

    client.force_authenticate(user=user)
    payload = _food_item_payload(unit.id, owner_inventory.id)
    response = client.post(reverse("inventory-food-items", args=[owner_inventory.id]), payload, format="json")

    assert response.status_code == 400
    assert response.json()["inventory"] == ["You can only add food items to your own inventory."]


@pytest.mark.django_db
def test_user_cannot_update_or_delete_another_users_item():
    client = APIClient()
    owner = factories.UserFactory()
    member = factories.UserFactory()
    household = factories.HouseholdFactory(user=owner, allow_member_item_visibility=True)
    owner.userprofile.household = household
    owner.userprofile.save(update_fields=["household"])
    member.userprofile.household = household
    member.userprofile.save(update_fields=["household"])

    inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=owner, inventory=inventory)
    item = factories.FoodItemFactory(user=owner, inventory=inventory)

    client.force_authenticate(user=member)
    patch_response = client.patch(reverse("food-item-detail", args=[item.id]), {"name": "Nope"}, format="json")
    delete_response = client.delete(reverse("food-item-detail", args=[item.id]))

    assert patch_response.status_code == 403
    assert delete_response.status_code == 403


@pytest.mark.django_db
def test_household_listing_respects_default_privacy():
    client = APIClient()
    owner = factories.UserFactory()
    member = factories.UserFactory()
    household = factories.HouseholdFactory(user=owner, allow_member_item_visibility=False)
    owner.userprofile.household = household
    owner.userprofile.save(update_fields=["household"])
    member.userprofile.household = household
    member.userprofile.save(update_fields=["household"])

    owner_inventory = factories.InventoryFactory(household=household)
    member_inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=owner, inventory=owner_inventory)
    factories.UserInventoryFactory(user=member, inventory=member_inventory)

    member_item = factories.FoodItemFactory(user=member, inventory=member_inventory)
    factories.FoodItemFactory(user=owner, inventory=owner_inventory)

    client.force_authenticate(user=member)
    response = client.get(reverse("household-food-items", args=[household.id]))

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [member_item.id]


@pytest.mark.django_db
def test_inventory_listing_respects_ownership_by_default():
    client = APIClient()
    owner = factories.UserFactory()
    member = factories.UserFactory()
    household = factories.HouseholdFactory(user=owner, allow_member_item_visibility=False)
    owner.userprofile.household = household
    owner.userprofile.save(update_fields=["household"])
    member.userprofile.household = household
    member.userprofile.save(update_fields=["household"])

    owner_inventory = factories.InventoryFactory(household=household)
    member_inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=owner, inventory=owner_inventory)
    factories.UserInventoryFactory(user=member, inventory=member_inventory)

    factories.FoodItemFactory(user=owner, inventory=owner_inventory)

    client.force_authenticate(user=member)
    response = client.get(reverse("inventory-food-items", args=[owner_inventory.id]))

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_visibility_toggle_enabled_members_can_see_others_items():
    client = APIClient()
    owner = factories.UserFactory()
    member = factories.UserFactory()
    household = factories.HouseholdFactory(user=owner, allow_member_item_visibility=True)
    owner.userprofile.household = household
    owner.userprofile.save(update_fields=["household"])
    member.userprofile.household = household
    member.userprofile.save(update_fields=["household"])

    owner_inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=owner, inventory=owner_inventory)
    owner_item = factories.FoodItemFactory(user=owner, inventory=owner_inventory)

    client.force_authenticate(user=member)
    list_response = client.get(reverse("household-food-items", args=[household.id]))
    detail_response = client.get(reverse("food-item-detail", args=[owner_item.id]))

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [owner_item.id]
    assert detail_response.status_code == 200


@pytest.mark.django_db
def test_visibility_toggle_disabled_members_cannot_see_others_items():
    client = APIClient()
    owner = factories.UserFactory()
    member = factories.UserFactory()
    household = factories.HouseholdFactory(user=owner, allow_member_item_visibility=False)
    owner.userprofile.household = household
    owner.userprofile.save(update_fields=["household"])
    member.userprofile.household = household
    member.userprofile.save(update_fields=["household"])

    owner_inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=owner, inventory=owner_inventory)
    owner_item = factories.FoodItemFactory(user=owner, inventory=owner_inventory)

    client.force_authenticate(user=member)
    list_response = client.get(reverse("household-food-items", args=[household.id]))
    detail_response = client.get(reverse("food-item-detail", args=[owner_item.id]))

    assert list_response.status_code == 200
    assert list_response.json() == []
    assert detail_response.status_code == 404


@pytest.mark.django_db
def test_household_create_rejects_inventory_not_in_household():
    client = APIClient()
    user = factories.UserFactory()
    household_one = factories.HouseholdFactory(user=user)
    household_two = factories.HouseholdFactory(user=user)
    user.userprofile.household = household_one
    user.userprofile.save(update_fields=["household"])

    inventory_two = factories.InventoryFactory(household=household_two)
    factories.UserInventoryFactory(user=user, inventory=inventory_two)
    unit = factories.MeasurementUnitFactory()

    client.force_authenticate(user=user)
    payload = _food_item_payload(unit.id, inventory_two.id)
    response = client.post(reverse("household-food-items", args=[household_one.id]), payload, format="json")

    assert response.status_code == 400
    assert response.json()["inventory"] == ["Inventory does not belong to this household."]


@pytest.mark.django_db
def test_inventory_route_create_rejects_payload_inventory_mismatch():
    client = APIClient()
    user = factories.UserFactory()
    household = factories.HouseholdFactory(user=user)
    user.userprofile.household = household
    user.userprofile.save(update_fields=["household"])

    route_inventory = factories.InventoryFactory(household=household)
    other_inventory = factories.InventoryFactory(household=household)
    factories.UserInventoryFactory(user=user, inventory=route_inventory)
    factories.UserInventoryFactory(user=user, inventory=other_inventory)

    unit = factories.MeasurementUnitFactory()
    payload = _food_item_payload(unit.id, other_inventory.id)

    client.force_authenticate(user=user)
    response = client.post(reverse("inventory-food-items", args=[route_inventory.id]), payload, format="json")

    assert response.status_code == 400
    assert response.json()["inventory"] == ["Inventory does not match the inventory route parameter."]
