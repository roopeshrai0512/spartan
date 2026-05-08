"""User model with role-based access for Spartan Gym."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with three roles: super_admin, admin, member."""

    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.MEMBER
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    # Granular admin permissions (managed by super admin)
    can_add_member = models.BooleanField(default=False)
    can_edit_member = models.BooleanField(default=False)
    can_delete_member = models.BooleanField(default=False)
    can_manage_plans = models.BooleanField(default=False)
    can_manage_classes = models.BooleanField(default=False)
    can_manage_payments = models.BooleanField(default=False)
    can_manage_testimonials = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Super admin always has every permission
        if self.role == self.Role.SUPER_ADMIN:
            self.can_add_member = True
            self.can_edit_member = True
            self.can_delete_member = True
            self.can_manage_plans = True
            self.can_manage_classes = True
            self.can_manage_payments = True
            self.can_manage_testimonials = True
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_admin_role(self):
        return self.role in (self.Role.SUPER_ADMIN, self.Role.ADMIN)

    @property
    def is_member(self):
        return self.role == self.Role.MEMBER

    @property
    def display_name(self):
        full = self.get_full_name()
        return full if full else self.username

    def __str__(self):
        return f"{self.display_name} ({self.get_role_display()})"
