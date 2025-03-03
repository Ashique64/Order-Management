from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group, Permission


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if password is None:
            password = self.make_random_password()
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class Owner(AbstractBaseUser, PermissionsMixin):
    SHOP_TYPE_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('liquor_store', 'Liquor Store')
    ]

    email = models.EmailField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    shop_type = models.CharField(max_length=20, choices=SHOP_TYPE_CHOICES, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    
    
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Owner', 'Owner'),
        ('Staff', 'Staff')
    ]

    SHOP_TYPE_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('liquor_store', 'Liquor Store')
    ]

    email = models.EmailField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Owner')
    shop_type = models.CharField(max_length=20, choices=SHOP_TYPE_CHOICES, null=True, blank=True)
    restaurant = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions_set', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.role == 'Owner':
            if not self.shop_type:
                raise ValueError('The shop_type field must be set for owners.')
        else:
            self.shop_type = None
            self.phone_number = None 
        super().save(*args, **kwargs)

    @property
    def display_phone_number(self):
        if self.role == 'Owner':
            return self.phone_number
        return None
    


class Restaurant(models.Model):
    restaurant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="restaurants",
        limit_choices_to={'role': 'Owner'}
    )

    def __str__(self):
        return f'[Id: {self.restaurant_id}] :- {self.name}'


class Staff(models.Model):
    name = models.CharField(max_length=255, null=False,
                            blank=False, default='Default Name')
    email = models.EmailField(unique=True, null=False, blank=False)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="staff")

    def __str__(self):
        return self.email

    @classmethod
    def is_staff(cls, email):
        return cls.objects.filter(email=email).exists()



class Category(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    class Meta:
        unique_together = ('restaurant', 'name')

    def __str__(self):
        return f'{self.name}'
    
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.category.name}'



# class SalesReport(models.Model):
#     restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="sales_reports")
#     date = models.DateField(auto_now_add=True)
#     total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)