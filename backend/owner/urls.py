from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LoginView,OwnerRestaurantsView,RestaurantStaffView,AddStaffView,CategoryListCreateView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view(), name='login'),
    path('restaurants/', OwnerRestaurantsView.as_view(), name='owner-restaurants'),
    path('restaurant/<int:restaurant_id>/staff/', RestaurantStaffView.as_view(), name='restaurant-staff'),
    path('staff/add/', AddStaffView.as_view(), name='add-staff'),
    path('restaurant/<int:restaurant_id>/categories/', CategoryListCreateView.as_view(), name='category-list'),
]
