from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Staff, Restaurant,Owner, Category, Product
from .serializers import StaffSerializer, LoginSerializer, RestaurantSerializer, StaffCreateSerializer, CategorySerializer, ProductSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        restaurant = serializer.validated_data['restaurant']

        try:
            user = Owner.objects.get(email=email)
            if restaurant.owner == user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Owner login successful',
                    'user': user.email,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'redirect': 'owner_dashboard'
                }, status=status.HTTP_200_OK)
        except Owner.DoesNotExist:
            pass

        try:
            staff = Staff.objects.get(email=email, restaurant=restaurant)
            refresh = RefreshToken.for_user(staff)
            return Response({
                'message': 'Staff login successful',
                'staff': staff.email,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'redirect': 'home_page'
            }, status=status.HTTP_200_OK)
        except Staff.DoesNotExist:
            return Response(
                {'error': 'Email does not match any user or staff for this restaurant'},
                status=status.HTTP_404_NOT_FOUND
            )
            
class OwnerRestaurantsView(generics.ListAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated] 
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        print(f"Authenticated user: {user}")

        if user:
            user_email = user.email
            print(f"User email: {user_email}")
        else:
            user_email = None

        if not user_email or not Owner.objects.filter(email=user_email).exists():
            print("User is not authenticated or not an owner.")
            return Restaurant.objects.none()

        print("User is authenticated and is an owner.")
        return Restaurant.objects.filter(owner=user)

    def list(self, request, *args, **kwargs):
        user = request.user
        print(f"Request user: {user}")

        if user:
            user_email = user.email
        else:
            user_email = None

        if not user_email or not Owner.objects.filter(email=user_email).exists():
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
        restaurant_names = [restaurant['name'] for restaurant in serializer.data]
        return Response({
            'message': 'Restaurants listing successful',
            'restaurants': restaurant_names,
        })

class RestaurantStaffView(generics.ListAPIView):
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        owner = self.request.user
        
        if not isinstance(owner, Owner):
            return Staff.objects.none()

        try:
            restaurant = Restaurant.objects.get(
                restaurant_id=restaurant_id,
                owner=owner
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
        


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        owner = self.request.user

        if not isinstance(owner, Owner):
            return Category.objects.none()

        try:
            restaurant = Restaurant.objects.get(restaurant_id=restaurant_id, owner=owner)
            return Category.objects.filter(restaurant=restaurant)
        except Restaurant.DoesNotExist:
            return Category.objects.none()
    
    def perform_create(self, serializer):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(restaurant_id=restaurant_id, owner=self.request.user)
            serializer.save(restaurant=restaurant)
        except Restaurant.DoesNotExist:
            raise serializer.ValidationError("Restaurant not found or you do not have permission to add categories to this restaurant.")


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        owner = self.request.user

        if not isinstance(owner, Owner):
            return Product.objects.none()

        try:
            category = Category.objects.get(id=category_id, restaurant__owner=owner)
            return Product.objects.filter(category=category)
        except Category.DoesNotExist:
            return Product.objects.none()
    
    def perform_create(self, serializer):
        category_id = self.kwargs.get('category_id')
        try:
            category = Category.objects.get(id=category_id, restaurant__owner=self.request.user)
            serializer.save(category=category)
        except Category.DoesNotExist:
            raise serializer.ValidationError("Category not found or you do not have permission to add products to this category.")