"""DRF API endpoints — used by the dashboard charts and public widgets."""
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.models import User

from .models import (
    Attendance, GymClass, Membership, Payment, Plan, ProgressLog, Testimonial, Trainer,
)
from .serializers import (
    AttendanceSerializer, GymClassSerializer, MembershipSerializer,
    PaymentSerializer, PlanSerializer, ProgressLogSerializer,
    TestimonialSerializer, TrainerSerializer,
)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_role


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_plans(request):
    qs = Plan.objects.filter(is_active=True)
    return Response(PlanSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_testimonials(request):
    qs = Testimonial.objects.filter(is_published=True)
    return Response(TestimonialSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_classes(request):
    qs = GymClass.objects.filter(is_active=True).select_related("trainer")
    return Response(GymClassSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_trainers(request):
    qs = Trainer.objects.filter(is_active=True)
    return Response(TrainerSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_summary(request):
    from datetime import date, timedelta
    from django.db.models import Sum
    today = date.today()
    week_revenue = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        rev = Payment.objects.filter(
            status=Payment.Status.PAID, paid_on__date=d,
        ).aggregate(t=Sum("amount"))["t"] or 0
        week_revenue.append({"day": d.strftime("%a"), "revenue": float(rev)})
    return Response({
        "members": User.objects.filter(role=User.Role.MEMBER).count(),
        "active_memberships": Membership.objects.filter(
            status=Membership.Status.ACTIVE, end_date__gte=today
        ).count(),
        "today_attendance": Attendance.objects.filter(check_in__date=today).count(),
        "month_revenue": float(
            Payment.objects.filter(
                status=Payment.Status.PAID, paid_on__month=today.month,
                paid_on__year=today.year,
            ).aggregate(t=Sum("amount"))["t"] or 0
        ),
        "week_revenue": week_revenue,
    })
