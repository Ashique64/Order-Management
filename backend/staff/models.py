from django.db import models
from owner.models import Staff,Product

# Create your models here.


class Order(models.Model):

    staff = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    def __str__(self):
        return f'Order #{self.id} by {self.staff.name}'
    
    def calculate_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_price = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    
    def __str__(self):
        return f'{self.quantity}x {self.product.name}'
    
    def get_subtotal(self):
        return self.quantity * self.price_at_time
