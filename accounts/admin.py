from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_active']
    list_filter = ['role', 'is_active', 'department']
    fieldsets = UserAdmin.fieldsets + (
        ('LASU Profile', {'fields': ('role', 'department', 'phone', 'staff_id', 'must_change_password')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('LASU Profile', {'fields': ('role', 'department', 'phone', 'staff_id')}),
    )
