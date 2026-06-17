from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    CustomUser,
    Role,
    Department,
    StaffProfile,
    Permission,
    RolePermission
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username',
        'email',
        'employee_id',
        'company',
        'branch',
        'role',
        'department',
        'is_active'
    )

    list_filter = (
        'company',
        'branch',
        'role',
        'department',
        'is_active'
    )

    search_fields = (
        'username',
        'email',
        'employee_id',
        'phone'
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name'
    )

    search_fields = (
        'name',
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name'
    )

    search_fields = (
        'name',
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'code'
    )

    search_fields = (
        'name',
        'code'
    )


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):

    list_display = (
        'role',
        'permission'
    )

    list_filter = (
        'role',
    )


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'joining_date',
        'reporting_manager',
        'is_active_employee'
    )

    list_filter = (
        'is_active_employee',
    )

    search_fields = (
        'user__username',
    )