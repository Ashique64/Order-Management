from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Restaurant, Category, Product, CustomUser
from .serializers import LoginSerializer, RestaurantSerializer, StaffCreateSerializer, CategorySerializer, ProductSerializer,CustomUserSerializer
from rest_framework.exceptions import PermissionDenied, NotFound


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        restaurant = serializer.validated_data['restaurant']


        try:
            user = CustomUser.objects.get(email=email)
            
            if user.restaurant is None:
                user.restaurant = restaurant
                user.save()
            
            if user.role == 'Owner' and user.restaurant == restaurant:
                refresh = RefreshToken.for_user(user)
                restaurant_data = RestaurantSerializer(restaurant).data
                return Response({
                    'message': 'Owner login successful',
                    'user': user.email,
                    'role':user.role,
                    'restaurant_id':restaurant_data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'redirect': 'owner_dashboard'
                }, status=status.HTTP_200_OK)
            elif user.role == 'Staff' and user.restaurant == restaurant:
                refresh = RefreshToken.for_user(user)
                restaurant_data = RestaurantSerializer(restaurant).data
                return Response({
                    'message': 'Staff login successful',
                    'user': user.email,
                    'role':user.role,
                    'restaurant_id':restaurant_data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'redirect': 'home_page'
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'User does not match the provided restaurant'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Email does not match any user'},
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

        if not user_email or not CustomUser.objects.filter(email=user_email, role='Owner').exists():
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

        if not user_email or not CustomUser.objects.filter(email=user_email).exists():
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
        # restaurant_names = [restaurant['name'] for restaurant in serializer.data]
        return Response({
            'message': 'Restaurants listing successful',
            'restaurants': serializer.data,
        })

class RestaurantStaffView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        owner = self.request.user

        if not owner or owner.role != 'Owner':
            return CustomUser.objects.none()

        try:
            restaurant = Restaurant.objects.get(
                restaurant_id=restaurant_id,
                owner=owner
            )
            return CustomUser.objects.filter(restaurant=restaurant, role='Staff')
        except Restaurant.DoesNotExist:
            return CustomUser.objects.none()

class AddStaffView(generics.CreateAPIView):
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        owner = self.request.user

        if owner.role != 'Owner':
            return Response(
                {'error': 'Only owners can add staff'},
                status=status.HTTP_403_FORBIDDEN
            )

        restaurant_id = request.data.get('restaurant_id')

        try:
            restaurant = Restaurant.objects.get(
                restaurant_id=restaurant_id,
                owner=owner
            )
        except Restaurant.DoesNotExist:
            return Response(
                {'error': 'Restaurant not found or does not belong to the owner'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(restaurant=restaurant)

        return Response(
            {'message': 'Staff added successfully', 'staff': serializer.data},
            status=status.HTTP_201_CREATED
        )
        
class StaffUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        staff_name = self.kwargs.get('name')
        user = self.request.user

        try:
            staff = CustomUser.objects.get(name=staff_name, role='Staff')
        except CustomUser.DoesNotExist:
            raise NotFound("Staff member not found.")

        if staff.restaurant.owner != user:
            raise PermissionDenied("You do not have permission to access this staff member.")

        return staff
        


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        user = self.request.user

        # if owner.role != 'Owner':
        #     return Category.objects.none()

        try:
            restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
            if user.role == 'Owner' and restaurant.owner == user:
                return Category.objects.filter(restaurant=restaurant)
            elif user.role == 'Staff' and user.restaurant == restaurant:
                return Category.objects.filter(restaurant=restaurant)
            else:
                return Category.objects.none()
            # return Category.objects.filter(restaurant=restaurant)
        except Restaurant.DoesNotExist:
            return Category.objects.none()
    
    def perform_create(self, serializer):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(restaurant_id=restaurant_id, owner=self.request.user)
            serializer.save(restaurant=restaurant)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Restaurant not found or you do not have permission to add categories to this restaurant.")

class CategoryUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        category_id = self.kwargs.get('pk')
        user = self.request.user

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise NotFound("Category not found.")

        restaurant_owner = category.restaurant.owner

        if user == restaurant_owner:
            return category
        else:
            raise PermissionDenied("You do not have permission to access this category.")


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        user = self.request.user

        # if owner.role != 'Owner':
        #     return Product.objects.none()

        # try:
        #     category = Category.objects.get(id=category_id, restaurant__owner=user)
        #     return Product.objects.filter(category=category)
        # except Category.DoesNotExist:
        #     return Product.objects.none()
        
        try:
            category = Category.objects.get(id=category_id)
            
            if user.role == 'Owner' and category.restaurant.owner == user:
                return Product.objects.filter(category=category)
            elif user.role == 'Staff' and user.restaurant == category.restaurant:
                return Product.objects.filter(category=category)
            else:
                return Product.objects.none()
        except Category.DoesNotExist:
            return Product.objects.none()
        
    
    def perform_create(self, serializer):
        category_id = self.kwargs.get('category_id')
        try:
            category = Category.objects.get(id=category_id, restaurant__owner=self.request.user)
            serializer.save(category=category)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category not found or you do not have permission to add products to this category.")
        

class ProductUpdataDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        product_id = self.kwargs.get('pk')
        user = self.request.user

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("Product not found.")

        restaurant_owner = product.category.restaurant.owner

        if user == restaurant_owner :
            return product
        else:
            raise PermissionDenied("You do not have permission to access this product.")