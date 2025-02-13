from django.urls import path
from .views import LoginView,OwnerRestaurantsView,RestaurantStaffView,AddStaffView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('restaurants/', OwnerRestaurantsView.as_view(), name='owner-restaurants'),
    path('restaurant/<int:restaurant_id>/staff/', RestaurantStaffView.as_view(), name='restaurant-staff'),
    path('staff/add/', AddStaffView.as_view(), name='add-staff'),
]
