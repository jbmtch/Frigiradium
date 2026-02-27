import pytest
import pdb

from inventory.tests.factories import factories
from inventory.models import UserInventory, UserProfile
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.mark.django_db
def test_inventory_list_returns_only_user_inventories():
    client = APIClient()
    user1 = factories.UserFactory()
    user2 = factories.UserFactory()
    household = factories.HouseholdFactory()

    inv1 = factories.InventoryFactory(household=household, name="Fridge")
    inv2 = factories.InventoryFactory(household=household, name="Freezer")

    factories.UserInventoryFactory.create(user=user1, inventory=inv1)
    factories.UserInventoryFactory.create(user=user2, inventory=inv2)

    client.force_authenticate(user=user1)
    url = reverse('inventory-list')
    response = client.get(url)

    assert response.status_code == 200
    names = [item['name'] for item in response.json()]

    assert "Fridge" in names
    assert "Freezer" not in names

@pytest.mark.django_db
def test_cannot_retrieve_inventory_unless_member():
    client = APIClient()
    member = factories.UserFactory()
    outsider = factories.UserFactory()
    household = factories.HouseholdFactory()

    inv = factories.InventoryFactory(household=household, name="Fridge")

    factories.UserInventoryFactory.create(user=member, inventory=inv)

    client.force_authenticate(user=outsider)
    url = reverse('inventory-detail', args=[inv.id])
    response = client.get(url)

    assert response.status_code in (403, 404)

@pytest.mark.django_db
def test_creating_inventory_adds_creator_as_member():
    client = APIClient()
    user = factories.UserFactory()
    household = factories.HouseholdFactory(user=user)

    client.force_authenticate(user=user)

    url = reverse('household-inventory', args=[household.id])

    payload = {"name":"Family Fridge"}
    response = client.post(url, payload, format='json')

    assert response.status_code == 201
    inv_id = response.json()['id']

    memberships = UserInventory.objects.filter(user=user, inventory_id=inv_id)
    assert memberships.count() == 1

@pytest.mark.django_db
def test_can_only_access_inventories_you_are_member_of():
    client = APIClient()
    member = factories.UserFactory()
    non_member_user = factories.UserFactory()
    household = factories.HouseholdFactory()

    inventory = factories.InventoryFactory(household=household)

    factories.UserInventoryFactory.create(user=member, inventory=inventory)

    client.force_authenticate(user=non_member_user)
    url = reverse('inventory-detail', args=[inventory.id])

    response = client.get(url)

    assert response.status_code == 404
    memberships = UserInventory.objects.filter(user=member, inventory=inventory)
    assert memberships.count() == 1 

@pytest.mark.django_db
def test_cannot_create_duplicate_user_inventory_association():
    client = APIClient()
    member = factories.UserFactory()
    household = factories.HouseholdFactory()
    inventory = factories.InventoryFactory(household=household)

    factories.UserInventoryFactory.create(user=member, inventory=inventory)

    # try to create another UserInventory object with same user / inventory 

    client.force_authenticate(user=member)
    url = reverse('userinventory-list')
    payload = {"user": member.id, "inventory": inventory.id }
    response = client.post(url, payload, format='json')

    assert response.status_code == 400
    assert response.json()['non_field_errors'] == [
        'This user is already associated with this inventory.'
    ]

@pytest.mark.django_db
def test_cannot_create_inventory_unless_member_of_household():
    client = APIClient()
    non_household_member = factories.UserFactory()
    household = factories.HouseholdFactory()

    client.force_authenticate(user=non_household_member)

    url = reverse("household-inventory", args=[household.id])
    payload = {"name": "Fridge"}
    response = client.post(url, payload, format='json')

    assert response.status_code == 403
    assert response.json()['detail'] == (
        'You must be a member of this household to create an inventory within it.'
    )

@pytest.mark.django_db
def test_cannot_add_non_household_member_to_inventory():
    client = APIClient()
    non_household_member = factories.UserFactory()
    household = factories.HouseholdFactory()
    inventory = factories.InventoryFactory()

    requester = household.user

    factories.UserInventoryFactory.create(user=requester, inventory=inventory)

    factories.HouseholdFactory(user=non_household_member)

    client.force_authenticate(user=requester)
    url = reverse('userinventory-list')
    payload = {"user": non_household_member.id, "inventory": inventory.id}
    response = client.post(url, payload, format='json')

    assert response.status_code == 400
    assert response.json()['non_field_errors'][0] == (
        'User must belong to the inventory\'s household to be added.'
    )

@pytest.mark.django_db
def test_can_add_household_member_to_inventory():
    client = APIClient()
    household_member = factories.UserFactory()
    household = factories.HouseholdFactory()
    inventory = factories.InventoryFactory(household=household)
    requester = household.user

    household_member_profile, created = UserProfile.objects.get_or_create(
        user=household_member,
        defaults={
            "zip_code": "00000",
            "phone_number": "0000000000",
            "household": household,
        },
    )
    if not created and household_member_profile.household_id != household.id:
        household_member_profile.household = household
        household_member_profile.save(update_fields=["household"])

    factories.UserInventoryFactory.create(user=requester, inventory=inventory)

    client.force_authenticate(user=requester)
    url = reverse('userinventory-list')
    payload = {"user": household_member.id, "inventory": inventory.id}
    response = client.post(url, payload, format='json')

    assert response.status_code == 201

@pytest.mark.django_db
def test_household_inventory_list_returns_only_that_household_when_member():
    client = APIClient()
    member = factories.UserFactory()
    household_one = factories.HouseholdFactory()
    household_two = factories.HouseholdFactory()

    inv_one = factories.InventoryFactory(household=household_one, name="Kitchen")
    inv_two = factories.InventoryFactory(household=household_two, name="Garage")

    factories.UserInventoryFactory.create(user=member, inventory=inv_one)
    factories.UserInventoryFactory.create(user=member, inventory=inv_two)

    client.force_authenticate(user=member)
    url = reverse("household-inventory", args=[household_one.id])
    response = client.get(url)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == inv_one.id
    assert payload[0]["name"] == "Kitchen"


@pytest.mark.django_db
def test_household_inventory_list_for_non_member_returns_empty_or_404_by_policy():
    client = APIClient()
    non_member = factories.UserFactory()
    household = factories.HouseholdFactory()
    factories.InventoryFactory(household=household)

    client.force_authenticate(user=non_member)
    url = reverse("household-inventory", args=[household.id])
    response = client.get(url)

    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert response.json() == []


@pytest.mark.django_db
def test_patch_userinventory_partial_update_requires_requester_membership():
    client = APIClient()
    requester = factories.UserFactory()
    member = factories.UserFactory()
    replacement_user = factories.UserFactory()
    household = factories.HouseholdFactory()
    inventory = factories.InventoryFactory(household=household)

    member.userprofile.household = household
    member.userprofile.save(update_fields=["household"])
    replacement_user.userprofile.household = household
    replacement_user.userprofile.save(update_fields=["household"])

    membership = factories.UserInventoryFactory.create(user=member, inventory=inventory)

    client.force_authenticate(user=requester)
    url = reverse("userinventory-detail", args=[membership.id])
    response = client.patch(url, {"user": replacement_user.id}, format="json")

    assert response.status_code in (403, 404)
    if response.status_code == 403:
        assert response.json()["detail"] == (
            "You must already be a member of this inventory to perform updates."
        )


@pytest.mark.django_db
def test_inventory_create_creates_exactly_one_membership_for_creator():
    client = APIClient()
    creator = factories.UserFactory()
    household = factories.HouseholdFactory(user=creator)

    client.force_authenticate(user=creator)
    url = reverse("household-inventory", args=[household.id])
    response = client.post(url, {"name": "Pantry"}, format="json")

    assert response.status_code == 201
    created_inventory_id = response.json()["id"]

    memberships = UserInventory.objects.filter(user=creator, inventory_id=created_inventory_id)
    assert memberships.count() == 1


@pytest.mark.django_db
def test_post_userinventory_requires_requester_membership_in_inventory():
    client = APIClient()
    requester = factories.UserFactory()
    target_user = factories.UserFactory()
    household = factories.HouseholdFactory()
    inventory = factories.InventoryFactory(household=household)

    target_user.userprofile.household = household
    target_user.userprofile.save(update_fields=["household"])

    client.force_authenticate(user=requester)
    url = reverse("userinventory-list")
    response = client.post(url, {"user": target_user.id, "inventory": inventory.id}, format="json")

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You must already be a member of this inventory to add members."
    )
