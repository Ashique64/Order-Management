from rest_framework import serializers
from .models import Staff, Restaurant,Owner


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['email', 'restaurant']

class RestaurantSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(many=True, read_only=True)
    class Meta:
        model = Restaurant
        fields = ['name', 'owner', 'staff']
        
        
class OwnerSerializer(serializers.ModelSerializer):
    restaurants = RestaurantSerializer(many=True, read_only=True)
    class Meta:
        model = Owner
        fields = ['email', 'restaurants']
        
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    restaurant_id = serializers.IntegerField(required=True)

    def validate(self, data):
        email = data.get('email')
        print(email)
        restaurant_id = data.get('restaurant_id')

        # try:
        #     email = Owner.objects.get(email=email) 
        # except Owner.DoesNotExist:
        #     raise serializers.ValidationError("Owner not found")

        # data['email'] = email

        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Restaurant not found")

        data['restaurant'] = restaurant
        
        return data