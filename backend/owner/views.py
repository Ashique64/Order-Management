from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Owner, Staff, Restaurant
from .serializers import OwnerSerializer, StaffSerializer, LoginSerializer


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        restaurant = serializer.validated_data['restaurant']

        if restaurant.owner.email == email:
            owner_serializer = OwnerSerializer(restaurant.owner)
            return Response(
                {
                    'message': 'Owner login successful',
                    'owner': owner_serializer.data['email'],
                    'redirect': 'owner_dashboard'
                },
                status=status.HTTP_200_OK
            )

        try:
            staff = Staff.objects.get(email=email, restaurant=restaurant)
            staff_serializer = StaffSerializer(staff)
            return Response(
                {
                    'message': 'Staff login successful',
                    'user': staff_serializer.data,
                    'redirect': 'home_page'
                },
                status=status.HTTP_200_OK
            )
        except Staff.DoesNotExist:
            return Response(
                {'error': 'Email does not match any owner or staff for this restaurant'},
                status=status.HTTP_404_NOT_FOUND
            )
