from rest_framework import serializers
from .models import Staff, Restaurant,Owner,Product,Category

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['name', 'email', 'restaurant']

class RestaurantSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Restaurant
        fields = ['restaurant_id', 'name', 'owner', 'staff']

class OwnerSerializer(serializers.ModelSerializer):
    restaurants = RestaurantSerializer(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ['email', 'name', 'phone_number', 'shop_type', 'restaurants']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    restaurant_id = serializers.IntegerField(required=True)

    def validate(self, data):
        email = data.get('email')
        restaurant_id = data.get('restaurant_id')

        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Restaurant not found")

        owner_exists = Owner.objects.filter(email=email).exists()
        staff_exists = Staff.objects.filter(email=email, restaurant=restaurant).exists()

        if not (owner_exists or staff_exists):
            raise serializers.ValidationError("Invalid email for this restaurant")

        data['restaurant'] = restaurant
        return data

class StaffCreateSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(write_only=True)
    restaurant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Staff
        fields = ['name', 'email', 'restaurant_id', 'owner_email']

    def create(self, validated_data):
        owner_email = validated_data.pop('owner_email')
        restaurant_id = validated_data.pop('restaurant_id')

        try:
            restaurant = Restaurant.objects.get(
                restaurant_id=restaurant_id,
                owner__email=owner_email
            )
            return Staff.objects.create(restaurant=restaurant, **validated_data)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Invalid restaurant or owner")
        



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'description', 'price', 'is_available', 'image', 'quantity']
        read_only_fields = ['category']



class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'restaurant', 'name', 'description', 'products', 'image']
        read_only_fields = ['restaurant']

