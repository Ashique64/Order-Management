from django.db import models
from django.contrib.auth.models import User

# Assuming you have already removed the custom Owner model

class Restaurant(models.Model):
    restaurant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurants")

    def __str__(self):
        return f'[Id: {self.restaurant_id}] :- {self.name}'
   
class Staff(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, default='Default Name')
    email = models.EmailField(unique=True, null=False, blank=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="staff")


    def __str__(self):
        return self.email

    @classmethod
    def is_staff(cls, email):
        return cls.objects.filter(email=email).exists()