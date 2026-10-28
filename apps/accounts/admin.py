from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import Customer, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('mobile_number', 'name', 'family', 'email', 'gender', 'is_active', 'is_admin')
    list_filter = ('is_active', 'is_admin')
    search_fields = ('mobile_number', 'name', 'family', 'email')
    ordering = ('mobile_number',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('اطلاعات شخصی', {'fields': ('name', 'family', 'email', 'gender', 'active_code')}),
        ('دسترسی‌ها', {
            'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('mobile_number', 'email', 'name', 'family', 'gender', 'password1', 'password2'),
        }),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__mobile_number', 'user__name', 'user__family', 'phone_number')
