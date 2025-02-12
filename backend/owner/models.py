from django.db import models

# Create your models here.

class Owner(models.Model):
    email = models.EmailField(unique=True, null=False, blank=False)
    
    def __str__(self):
        return self.email
    
    @classmethod
    def is_owner(cls, email):
        return cls.objects.filter(email=email).exists()

class Restaurant(models.Model):
    restaurant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="restaurants")
    
    def __str__(self):
        return self.name
   
class Staff(models.Model):
    email = models.EmailField(unique=True, null=False, blank=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="staff")
    
    def __str__(self):
        return self.email
    
    @classmethod
    def is_staff(cls, email):
        return cls.objects.filter(email=email).exists()
    



# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Owner, Staff, Restaurant
# from .serializers import LoginSerializer

# class LoginView(APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         email = serializer.validated_data['email']
#         restaurant_id = serializer.validated_data['restaurant_id']

#         # Check if the restaurant exists
#         try:
#             restaurant = Restaurant.objects.get(pk=restaurant_id)
#         except Restaurant.DoesNotExist:
#             return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

#         # Check if the email belongs to an owner
#         if Owner.is_owner(email):
#             return Response({'message': 'Owner login successful', 'redirect': 'owner_dashboard'}, status=status.HTTP_200_OK)

#         # Check if the email belongs to a staff member of the specified restaurant
#         if Staff.is_staff(email) and Staff.objects.filter(email=email, restaurant=restaurant).exists():
#             return Response({'message': 'Staff login successful', 'redirect': 'home_page'}, status=status.HTTP_200_OK)

#         # If the email doesn't belong to an owner or staff
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)