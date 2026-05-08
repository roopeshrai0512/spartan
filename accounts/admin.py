"""Django admin registration for the User model."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "first_name", "last_name", "is_active")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone")

    fieldsets = UserAdmin.fieldsets + (
        ("Spartan Profile", {"fields": ("role", "phone", "avatar", "date_of_birth", "address")}),
        (
            "Granular Admin Permissions",
            {
                "fields": (
                    "can_add_member",
                    "can_edit_member",
                    "can_delete_member",
                    "can_manage_plans",
                    "can_manage_classes",
                    "can_manage_payments",
                    "can_manage_testimonials",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Spartan Profile", {"fields": ("role", "email", "phone")}),
    )
