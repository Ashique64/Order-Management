from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_subtotal'
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price_at_time', 'subtotal']
        read_only_fields = ['price_at_time']

    def create(self, validated_data):
        validated_data['price_at_time'] = validated_data['product'].price
        return super().create(validated_data)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    staff_name = serializers.CharField(source='staff.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'staff', 'staff_name', 'order_date', 'total_price', 'items']
        read_only_fields = ['order_date', 'total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                quantity=item_data['quantity'],
                price_at_time=item_data['product'].price
            )
        
        order.calculate_total()
        return order
