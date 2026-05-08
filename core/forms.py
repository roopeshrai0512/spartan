"""Forms for the core app."""
from django import forms

from accounts.forms import BootstrapMixin
from .models import (
    ContactMessage, GymClass, Membership, Payment, Plan,
    ProgressLog, SiteSettings, Testimonial, Trainer,
)


class PlanForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Plan
        fields = ("name", "tier", "price", "duration_days", "features", "is_featured", "is_active", "color", "icon")
        widgets = {"features": forms.Textarea(attrs={"rows": 5})}


class TrainerForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ("name", "title", "specialty", "bio", "photo", "instagram", "years_experience", "is_active")
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}


class GymClassForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = GymClass
        fields = ("name", "description", "trainer", "day_of_week", "start_time", "duration_minutes", "capacity", "level", "icon", "color", "is_active")
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class TestimonialForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ("author_name", "author_role", "photo", "quote", "rating", "is_published", "is_featured")
        widgets = {"quote": forms.Textarea(attrs={"rows": 4})}


class TestimonialMemberForm(BootstrapMixin, forms.ModelForm):
    """Members can submit testimonials (admin will approve)."""
    class Meta:
        model = Testimonial
        fields = ("quote", "rating")
        widgets = {"quote": forms.Textarea(attrs={"rows": 4, "placeholder": "Share your Spartan story…"})}


class MembershipForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Membership
        fields = ("member", "plan", "start_date", "status", "notes")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class PaymentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("member", "membership", "amount", "method", "status", "note")
        widgets = {"note": forms.Textarea(attrs={"rows": 2})}


class ProgressLogForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ProgressLog
        fields = ("logged_on", "weight_kg", "height_cm", "body_fat", "note")
        widgets = {"logged_on": forms.DateInput(attrs={"type": "date"})}


class ContactForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}


class SiteSettingsForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = "__all__"
        widgets = {"about": forms.Textarea(attrs={"rows": 4})}
