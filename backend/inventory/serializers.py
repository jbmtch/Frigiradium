from inventory.models import UserProfile, Household, Inventory, UserInventory
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class HouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = '__all__'
        read_only_fields = ('user',)

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id', 'name', 'household', 'created_at', 'updated_at']
        read_only_fields = ('id', 'created_at', 'updated_at', 'household')

class UserInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInventory
        fields = '__all__'
        
        validators = [
            UniqueTogetherValidator(
                queryset=UserInventory.objects.all(),
                fields=['user', 'inventory'],
                message='This user is already associated with this inventory.'
            )
        ]

    def validate(self, attrs):
        inventory = attrs.get('inventory', getattr(self.instance, 'inventory', None))
        user = attrs.get('user', getattr(self.instance, 'user', None))

        if not inventory or not user:
            return attrs

        household = inventory.household
        if household is None:
            raise serializers.ValidationError("Inventories must belong to a household.")
        
        is_owner = household.user_id == user.id
        is_member = household.members.filter(user=user).exists()

        if not (is_owner or is_member):
            raise serializers.ValidationError(
                "User must belong to the inventory's household to be added."
            )




