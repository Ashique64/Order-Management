from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Owner,Restaurant
from .forms import OwnerCreationForm, OwnerChangeForm

class OwnerAdmin(UserAdmin):
    add_form = OwnerCreationForm
    form = OwnerChangeForm
    model = Owner

    list_display = ('email', 'name', 'phone_number', 'shop_type', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'shop_type')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone_number', 'shop_type')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone_number', 'shop_type', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    

admin.site.register(Owner, OwnerAdmin)
admin.site.register(Restaurant)