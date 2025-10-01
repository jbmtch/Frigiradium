import pytest
from django.contrib.auth.models import User
from inventory.models import Household, UserProfile
from inventory.tests.factories import factories


@pytest.mark.django_db
def test_user_profile_created_on_user_creation():
    user = factories.UserFactory()

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        pytest.fail("UserProfile was not created for the new user")

    assert profile.user == user


@pytest.mark.django_db
def test_user_creation_requires_username():
    with pytest.raises(ValueError, match="must be set"):
        User.objects.create_user(username="", password="testpass")


@pytest.mark.django_db
def test_user_creation_requires_password():
    user = User.objects.create_user(username="testuser", password=None)

    assert user.has_usable_password() is False


@pytest.mark.django_db
def test_updated_at_changes_on_profile_update():
    user = User.objects.create_user(username="timestamptest", password="abc123")
    profile = user.userprofile

    original_updated_at = profile.updated_at

    profile.zip_code = "90083"
    profile.save()

    profile.refresh_from_db()

    assert profile.updated_at > original_updated_at


@pytest.mark.django_db
def test_user_profile_assigned_to_household():
    user = User.objects.create_user(username="testuser", password="abc123")
    household = Household.objects.create(name="Test Household")

    profile = user.userprofile
    profile.household = household
    profile.save()

    assert profile.household is not None
    assert profile.household.name == "Test Household"
    assert household.members.filter(user=user).exists()
