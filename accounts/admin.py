from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class SchobrasUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Rol en el panel", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Rol en el panel", {"fields": ("role",)}),)
