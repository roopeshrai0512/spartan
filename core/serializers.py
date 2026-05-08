"""DRF serializers for the public/internal API."""
from rest_framework import serializers

from accounts.models import User
from .models import (
    Attendance, ClassBooking, GymClass, Membership, Payment,
    Plan, ProgressLog, Testimonial, Trainer,
)


class PlanSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ("id", "name", "tier", "price", "duration_days", "features",
                  "is_featured", "color", "icon")

    def get_features(self, obj):
        return obj.feature_list()


class TrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = ("id", "name", "title", "specialty", "bio", "years_experience", "instagram")


class GymClassSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source="trainer.name", read_only=True)
    day = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = GymClass
        fields = ("id", "name", "description", "trainer_name", "day", "start_time",
                  "duration_minutes", "capacity", "level", "icon", "color")


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ("id", "author_name", "author_role", "quote", "rating", "is_featured")


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "phone", "role", "is_active")


class MembershipSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    member_name = serializers.CharField(source="member.display_name", read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = Membership
        fields = ("id", "member_name", "plan", "start_date", "end_date", "status", "days_remaining")


class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.display_name", read_only=True)

    class Meta:
        model = Attendance
        fields = ("id", "member_name", "check_in", "check_out", "note")


class PaymentSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.display_name", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "member_name", "amount", "method", "status", "paid_on", "note")


class ProgressLogSerializer(serializers.ModelSerializer):
    bmi = serializers.FloatField(read_only=True)

    class Meta:
        model = ProgressLog
        fields = ("id", "logged_on", "weight_kg", "height_cm", "body_fat", "bmi", "note")
