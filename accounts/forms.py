"""Auth forms for Spartan Gym."""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs["class"] = (existing + " form-check-input").strip()
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = (existing + " form-select").strip()
            else:
                field.widget.attrs["class"] = (existing + " form-control").strip()
            if not field.widget.attrs.get("placeholder"):
                field.widget.attrs["placeholder"] = field.label or name.title()


class LoginForm(BootstrapMixin, AuthenticationForm):
    pass


class RegisterForm(BootstrapMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=80, required=True)
    last_name = forms.CharField(max_length=80, required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.MEMBER
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone = self.cleaned_data.get("phone", "")
        if commit:
            user.save()
        return user


class ProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "address", "date_of_birth", "avatar")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class AdminUserForm(BootstrapMixin, forms.ModelForm):
    """Used by super-admin to manage admin permissions."""
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep existing.")

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email", "phone", "role", "is_active",
            "can_add_member", "can_edit_member", "can_delete_member",
            "can_manage_plans", "can_manage_classes", "can_manage_payments", "can_manage_testimonials",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user


class MemberCreateForm(BootstrapMixin, forms.ModelForm):
    """Form admins use to create new members/students."""
    password = forms.CharField(widget=forms.PasswordInput, min_length=4)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone", "address", "date_of_birth", "avatar", "password")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 2}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.MEMBER
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class MemberEditForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "address", "date_of_birth", "avatar", "is_active")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 2}),
        }
