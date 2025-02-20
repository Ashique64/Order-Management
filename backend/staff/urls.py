from django.urls import path
from .views import OrderListCreateView, OrderDetailView, add_item, remove_item,print_bill

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/increase-item/', add_item, name='add-item'),
    path('orders/<int:order_id>/decrease-item/', remove_item, name='remove-item'),
    path('/print-bill/{order_id}/', print_bill, name='print-bill'),
]
