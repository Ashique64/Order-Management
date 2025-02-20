from rest_framework import serializers
from .models import Staff, Restaurant,Owner,Product,Category,CustomUser




class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','email', 'name', 'phone_number', 'role', 'shop_type', 'restaurant']

class RestaurantSerializer(serializers.ModelSerializer):
    users = CustomUserSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Restaurant
        fields = ['restaurant_id', 'name', 'owner', 'staff','users']

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
        
        user_exists = CustomUser.objects.filter(email=email).exists()
        restaurent_exists = Restaurant.objects.filter(restaurant_id=restaurant_id).exists()

        if not user_exists and restaurent_exists:
            raise serializers.ValidationError("Invalid email for this restaurant")

        data['restaurant'] = restaurant
        return data

class StaffCreateSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'restaurant_id']

    def create(self, validated_data):
        restaurant_id = validated_data.pop('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Invalid restaurant")

        validated_data['restaurant'] = restaurant
        return CustomUser.objects.create(role='Staff', **validated_data)
        


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'description', 'price', 'is_available', 'image']
        read_only_fields = ['category']



class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'restaurant', 'name', 'description', 'products', 'image']
        read_only_fields = ['restaurant']

