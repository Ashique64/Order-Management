from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Restaurant, CustomUser
from .forms import OwnerCreationForm, OwnerChangeForm

class OwnerAdmin(UserAdmin):
    add_form = OwnerCreationForm
    form = OwnerChangeForm
    model = CustomUser

    list_display = ('email', 'name', 'phone_number', 'shop_type', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'shop_type', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone_number', 'role', 'shop_type')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone_number', 'shop_type', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='Owner')

admin.site.register(CustomUser, OwnerAdmin)
admin.site.register(Restaurant)
