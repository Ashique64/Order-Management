from django.urls import path
from .views import OrderListCreateView, OrderDetailView, add_item, remove_item

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/add-item/', add_item, name='add-item'),
    path('orders/<int:order_id>/remove-item/', remove_item, name='remove-item'),
]
