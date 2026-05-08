"""Django admin registration for core models."""
from django.contrib import admin

from .models import (
    Attendance, ClassBooking, ContactMessage, GymClass, Membership,
    Payment, Plan, ProgressLog, SiteSettings, Testimonial, Trainer,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("gym_name", "phone", "email")


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "specialty", "years_experience", "is_active")
    list_filter = ("is_active", "specialty")
    search_fields = ("name", "specialty")


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "price", "duration_days", "is_featured", "is_active")
    list_filter = ("tier", "is_featured", "is_active")
    search_fields = ("name",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("member", "plan", "start_date", "end_date", "status")
    list_filter = ("status", "plan")
    search_fields = ("member__username", "member__first_name", "member__last_name")
    autocomplete_fields = ("member", "plan", "created_by")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "rating", "is_published", "is_featured", "created_at")
    list_filter = ("is_published", "is_featured", "rating")
    search_fields = ("author_name", "quote")


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ("name", "trainer", "day_of_week", "start_time", "level", "capacity", "is_active")
    list_filter = ("level", "day_of_week", "is_active")
    search_fields = ("name",)


@admin.register(ClassBooking)
class ClassBookingAdmin(admin.ModelAdmin):
    list_display = ("gym_class", "member", "booked_at", "attended")
    list_filter = ("attended", "gym_class")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("member", "check_in", "check_out")
    list_filter = ("check_in",)
    search_fields = ("member__username",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "method", "status", "paid_on")
    list_filter = ("status", "method")
    search_fields = ("member__username", "member__first_name", "member__last_name")
    autocomplete_fields = ("member", "membership", "recorded_by")


@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
    list_display = ("member", "logged_on", "weight_kg", "height_cm")
    search_fields = ("member__username",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "handled", "created_at")
    list_filter = ("handled",)
    search_fields = ("name", "email", "subject")
