"""Core models for Spartan Gym Management."""
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class SiteSettings(models.Model):
    """Single-row settings — gym contact info shown across the site."""
    gym_name = models.CharField(max_length=120, default="Spartan Gym")
    tagline = models.CharField(max_length=200, default="Forge your strength. Embrace the warrior.")
    about = models.TextField(default="Spartan Gym is more than a gym — it's a brotherhood of athletes pushing the limits.")
    address = models.CharField(max_length=255, default="123 Warrior St, Athens, GR")
    phone = models.CharField(max_length=40, default="+1 (555) 010-7777")
    email = models.EmailField(default="contact@spartangym.com")
    instagram = models.URLField(blank=True, default="https://instagram.com/spartangym")
    facebook = models.URLField(blank=True, default="https://facebook.com/spartangym")
    twitter = models.URLField(blank=True, default="https://twitter.com/spartangym")
    hours = models.CharField(max_length=120, default="Mon-Sat 5:00 - 23:00 | Sun 7:00 - 21:00")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.gym_name

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Trainer(models.Model):
    name = models.CharField(max_length=120)
    title = models.CharField(max_length=120, default="Strength Coach")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="trainers/", blank=True, null=True)
    specialty = models.CharField(max_length=120, blank=True, help_text="e.g. CrossFit, Boxing, Yoga")
    instagram = models.URLField(blank=True)
    years_experience = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — {self.title}"


class Plan(models.Model):
    class Tier(models.TextChoices):
        BASIC = "basic", "Basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"
        ELITE = "elite", "Elite"

    name = models.CharField(max_length=80)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.BASIC)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    features = models.TextField(help_text="One feature per line.")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=20, default="#c8102e", help_text="Accent color for the card.")
    icon = models.CharField(max_length=40, default="bi-lightning-charge", help_text="Bootstrap icon name.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("price",)

    def __str__(self):
        return f"{self.name} (${self.price}/{self.duration_days}d)"

    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class Membership(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        PENDING = "pending", "Pending"

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="memberships")
    start_date = models.DateField(default=date.today)
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="memberships_created",
    )

    class Meta:
        ordering = ("-start_date",)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def refresh_status(self):
        if self.status == self.Status.CANCELLED:
            return
        self.status = self.Status.ACTIVE if self.end_date >= date.today() else self.Status.EXPIRED

    @property
    def days_remaining(self):
        return max(0, (self.end_date - date.today()).days)

    @property
    def is_active_now(self):
        return self.status == self.Status.ACTIVE and self.end_date >= date.today()

    def __str__(self):
        return f"{self.member.display_name} - {self.plan.name}"


class Testimonial(models.Model):
    author_name = models.CharField(max_length=120)
    author_role = models.CharField(max_length=120, blank=True, help_text="e.g. Member since 2023")
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="testimonials",
    )

    class Meta:
        ordering = ("-is_featured", "-created_at")

    def __str__(self):
        return f"{self.author_name} ({self.rating}★)"

    def stars(self):
        return range(self.rating)


class GymClass(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        ALL = "all", "All Levels"

    name = models.CharField(max_length=120)
    description = models.TextField()
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, related_name="classes")
    day_of_week = models.PositiveSmallIntegerField(
        choices=[(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"),
                 (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday")],
    )
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    capacity = models.PositiveIntegerField(default=20)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.ALL)
    icon = models.CharField(max_length=40, default="bi-activity")
    color = models.CharField(max_length=20, default="#c8102e")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("day_of_week", "start_time")

    def __str__(self):
        return f"{self.name} ({self.get_day_of_week_display()} {self.start_time})"


class ClassBooking(models.Model):
    gym_class = models.ForeignKey(GymClass, on_delete=models.CASCADE, related_name="bookings")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="class_bookings")
    booked_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ("gym_class", "member")
        ordering = ("-booked_at",)

    def __str__(self):
        return f"{self.member.display_name} → {self.gym_class.name}"


class Attendance(models.Model):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_records")
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ("-check_in",)

    def __str__(self):
        return f"{self.member.display_name} @ {self.check_in:%Y-%m-%d %H:%M}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        PENDING = "pending", "Pending"
        REFUNDED = "refunded", "Refunded"

    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Credit Card"
        UPI = "upi", "UPI / Wallet"
        BANK = "bank", "Bank Transfer"

    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CARD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PAID)
    note = models.CharField(max_length=200, blank=True)
    paid_on = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="payments_recorded",
    )

    class Meta:
        ordering = ("-paid_on",)

    def __str__(self):
        return f"${self.amount} - {self.member.display_name}"


class ProgressLog(models.Model):
    """Member self-tracked progress (weight, BMI, etc)."""
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_logs")
    logged_on = models.DateField(default=date.today)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2)
    body_fat = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ("-logged_on",)

    @property
    def bmi(self):
        if not self.height_cm or float(self.height_cm) == 0:
            return Decimal("0")
        h = float(self.height_cm) / 100.0
        return round(float(self.weight_kg) / (h * h), 1)

    def __str__(self):
        return f"{self.member.display_name} {self.logged_on} {self.weight_kg}kg"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    handled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name}: {self.subject}"
