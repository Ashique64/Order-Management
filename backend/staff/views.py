from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from owner.models import Staff, Restaurant,Product

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'restaurants'):
            restaurant_ids = user.restaurants.values_list('restaurant_id', flat=True)
            return Order.objects.filter(
                staff__restaurant_id__in=restaurant_ids
            ).order_by('-order_date')

        staff = Staff.objects.filter(email=user.email).first()
        if staff:
            return Order.objects.filter(staff=staff).order_by('-order_date')

        return Order.objects.none()

    def perform_create(self, serializer):
        
        staff = Staff.objects.filter(email=self.request.user.email).first()
        if not staff:
            raise serializer.ValidationError("Only staff members can create orders")

        items_data = self.request.data.get('items', [])
        restaurant_id = staff.restaurant_id

        for item in items_data:
            product_id = item.get('product')
            product = get_object_or_404(Product, id=product_id)
            if product.category.restaurant_id != restaurant_id:
                raise serializer.ValidationError(
                    f"Product {product.name} does not belong to your restaurant"
                )

        serializer.save(staff=staff)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item(request, order_id):
    
    order = get_object_or_404(Order, id=order_id)
    serializer = OrderItemSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(
            order=order,
            price_at_time=serializer.validated_data['product'].price
        )
        order.calculate_total()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_item(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    item_id = request.data.get('item_id')

    if not item_id:
        return Response(
            {"error": "item_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        item = order.items.get(id=item_id)
        item.delete()
        order.calculate_total()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )
    except OrderItem.DoesNotExist:
        return Response(
            {"error": "Item not found in order"},
            status=status.HTTP_404_NOT_FOUND
        )
