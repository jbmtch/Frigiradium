import pytest
import pdb

from inventory.tests.factories import factories
from inventory.models import UserInventory
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
    pdb.set_trace()
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











