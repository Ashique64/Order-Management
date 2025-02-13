from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Owner, Staff, Restaurant
from .serializers import OwnerSerializer, StaffSerializer, LoginSerializer, StaffSerializer, RestaurantSerializer, StaffCreateSerializer
from rest_framework.permissions import IsAuthenticated


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        restaurant = serializer.validated_data['restaurant']

        try:
            owner = Owner.objects.get(email=email)
            if restaurant.owner == owner:

                request.session['user_email'] = email
                request.session['user_type'] = 'owner'

                owner_serializer = OwnerSerializer(owner)
                return Response(
                    {
                        'message': 'Owner login successful',
                        'owner': owner_serializer.data['email'],
                        'redirect': 'owner_dashboard'
                    },
                    status=status.HTTP_200_OK
                )
        except Owner.DoesNotExist:
            pass

        try:
            staff = Staff.objects.get(email=email, restaurant=restaurant)

            request.session['user_email'] = email
            request.session['user_type'] = 'staff'

            staff_serializer = StaffSerializer(staff)
            return Response(
                {
                    'message': 'Staff login successful',
                    'staff': staff_serializer.data,
                    'redirect': 'home_page'
                },
                status=status.HTTP_200_OK
            )
        except Staff.DoesNotExist:
            return Response(
                {'error': 'Email does not match any owner or staff for this restaurant'},
                status=status.HTTP_404_NOT_FOUND
            )


class OwnerRestaurantsView(generics.ListAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_email = self.request.session.get('user_email')
        user_type = self.request.session.get('user_type')

        if not user_email or user_type != 'owner':
            return Restaurant.objects.none()

        return Restaurant.objects.filter(owner__email=user_email)

    def list(self, request, *args, **kwargs):
        user_email = request.session.get('user_email')
        user_type = request.session.get('user_type')

        if not user_email or user_type != 'owner':
            return Response(
                {'error': 'You must be logged in as an owner to view restaurants'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {'message': 'No restaurants found for your account'},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(queryset, many=True)
        restaurant_names = [restaurant['name']
                            for restaurant in serializer.data]
        return Response({
            'message': 'Restaurants listing successful',
            'restaurants': restaurant_names,
        },)


class RestaurantStaffView(generics.ListAPIView):
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        owner_email = self.request.query_params.get('owner_email')

        try:
            restaurant = Restaurant.objects.get(
                restaurant_id=restaurant_id,
                owner__email=owner_email
            )
            return Staff.objects.filter(restaurant=restaurant)
        except Restaurant.DoesNotExist:
            return Staff.objects.none()


class AddStaffView(generics.CreateAPIView):
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        owner_email = request.data.get('owner_email')
        restaurant_id = request.data.get('restaurant_id')

        try:
            restaurant = Restaurant.objects.get(
                restaurant_id=restaurant_id,
                owner__email=owner_email
            )
        except Restaurant.DoesNotExist:
            return Response(
                {'error': 'Restaurant not found or does not belong to the owner'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'message': 'Staff added successfully', 'staff': serializer.data},
            status=status.HTTP_201_CREATED
        )
