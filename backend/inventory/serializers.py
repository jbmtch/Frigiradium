from inventory.models import UserProfile, Household, Inventory, UserInventory, FoodItem
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user',)

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

        return attrs


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = [
            'id',
            'name',
            'category',
            'user',
            'inventory',
            'storage_type',
            'expiration_date',
            'date_opened',
            'date_frozen',
            'date_purchased',
            'isMeal',
            'date_refridgerated',
            'amount',
            'unit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def validate_inventory(self, inventory):
        request = self.context['request']
        if not inventory.memberships.filter(user=request.user).exists():
            raise serializers.ValidationError("You can only add food items to your own inventory.")
        return inventory

    def validate(self, attrs):
        inventory = attrs.get('inventory', getattr(self.instance, 'inventory', None))
        request = self.context['request']
        household_id = self.context.get('household_id')
        inventory_id = self.context.get('inventory_id')

        if household_id is not None and inventory and inventory.household_id != household_id:
            raise serializers.ValidationError({'inventory': ['Inventory does not belong to this household.']})

        if inventory_id is not None and inventory and inventory.id != inventory_id:
            raise serializers.ValidationError({'inventory': ['Inventory does not match the inventory route parameter.']})

        if self.instance and self.instance.user_id != request.user.id:
            raise serializers.ValidationError('You can only modify your own food items.')

        return attrs


