from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    CustomUser,
    Role,
    Department,
    StaffProfile
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass


admin.site.register(Role)
admin.site.register(Department)
admin.site.register(StaffProfile)