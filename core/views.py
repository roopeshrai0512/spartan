"""All views for the Spartan Gym site."""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.forms import AdminUserForm, MemberCreateForm, MemberEditForm
from accounts.models import User

from .decorators import admin_required, perm_required, super_admin_required
from .forms import (
    ContactForm, GymClassForm, MembershipForm, PaymentForm, PlanForm,
    ProgressLogForm, SiteSettingsForm, TestimonialForm, TestimonialMemberForm,
    TrainerForm,
)
from .models import (
    Attendance, ClassBooking, ContactMessage, GymClass, Membership,
    Payment, Plan, ProgressLog, SiteSettings, Testimonial, Trainer,
)


# ---------- PUBLIC ----------

def home(request):
    plans = Plan.objects.filter(is_active=True)[:4]
    testimonials = Testimonial.objects.filter(is_published=True)[:6]
    trainers = Trainer.objects.filter(is_active=True)[:4]
    classes = GymClass.objects.filter(is_active=True)[:6]
    stats = {
        "members": User.objects.filter(role=User.Role.MEMBER, is_active=True).count(),
        "trainers": Trainer.objects.filter(is_active=True).count(),
        "classes": GymClass.objects.filter(is_active=True).count(),
        "plans": Plan.objects.filter(is_active=True).count(),
    }
    return render(request, "core/home.html", {
        "plans": plans, "testimonials": testimonials,
        "trainers": trainers, "classes": classes, "stats": stats,
    })


def about(request):
    trainers = Trainer.objects.filter(is_active=True)
    return render(request, "core/about.html", {"trainers": trainers})


def plans(request):
    plans_qs = Plan.objects.filter(is_active=True)
    return render(request, "core/plans.html", {"plans": plans_qs})


def classes_public(request):
    classes_qs = GymClass.objects.filter(is_active=True).select_related("trainer")
    days = {}
    for c in classes_qs:
        days.setdefault(c.get_day_of_week_display(), []).append(c)
    return render(request, "core/classes.html", {"days": days})


def trainers_public(request):
    trainers_qs = Trainer.objects.filter(is_active=True)
    return render(request, "core/trainers.html", {"trainers": trainers_qs})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Message sent — we'll get back to you soon.")
            return redirect("core:contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})


# ---------- DASHBOARD ROUTER ----------

@login_required
def dashboard(request):
    if request.user.is_admin_role:
        return redirect("core:admin_dashboard")
    return redirect("core:my_membership")


# ---------- MEMBER PORTAL ----------

@login_required
def my_membership(request):
    active = (
        Membership.objects.filter(member=request.user)
        .select_related("plan").order_by("-start_date").first()
    )
    if active:
        active.refresh_status()
        active.save(update_fields=["status"])
    history = Membership.objects.filter(member=request.user).select_related("plan")[:10]
    payments = Payment.objects.filter(member=request.user)[:10]
    plans_qs = Plan.objects.filter(is_active=True)
    return render(request, "member/membership.html", {
        "active": active, "history": history, "plans": plans_qs, "payments": payments,
    })


@login_required
def subscribe_plan(request, plan_id):
    if not request.user.is_member:
        messages.error(request, "Only members can subscribe.")
        return redirect("core:dashboard")
    plan = get_object_or_404(Plan, pk=plan_id, is_active=True)
    today = date.today()
    membership = Membership.objects.create(
        member=request.user, plan=plan, start_date=today,
        end_date=today + timedelta(days=plan.duration_days),
        status=Membership.Status.ACTIVE,
    )
    Payment.objects.create(
        member=request.user, membership=membership, amount=plan.price,
        method=Payment.Method.CARD, status=Payment.Status.PAID,
        note=f"Subscription to {plan.name}",
    )
    messages.success(request, f"You're now subscribed to {plan.name}. Time to train!")
    return redirect("core:my_membership")


@login_required
def my_classes(request):
    bookings = ClassBooking.objects.filter(member=request.user).select_related("gym_class", "gym_class__trainer")
    booked_ids = set(bookings.values_list("gym_class_id", flat=True))
    classes_qs = GymClass.objects.filter(is_active=True).select_related("trainer")
    return render(request, "member/classes.html", {
        "bookings": bookings, "classes": classes_qs, "booked_ids": booked_ids,
    })


@login_required
def book_class(request, class_id):
    gym_class = get_object_or_404(GymClass, pk=class_id, is_active=True)
    booking, created = ClassBooking.objects.get_or_create(gym_class=gym_class, member=request.user)
    if created:
        messages.success(request, f"Booked {gym_class.name}.")
    else:
        messages.info(request, "You already booked this class.")
    return redirect("core:my_classes")


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(ClassBooking, pk=booking_id, member=request.user)
    booking.delete()
    messages.success(request, "Booking cancelled.")
    return redirect("core:my_classes")


@login_required
def member_check_in(request):
    if request.method == "POST":
        Attendance.objects.create(member=request.user, note="Self check-in")
        messages.success(request, "Checked in. Have a great workout!")
        return redirect("core:my_attendance")
    return redirect("core:my_attendance")


@login_required
def my_attendance(request):
    records = Attendance.objects.filter(member=request.user)[:60]
    today_count = Attendance.objects.filter(
        member=request.user, check_in__date=date.today()
    ).count()
    month_count = Attendance.objects.filter(
        member=request.user, check_in__month=date.today().month,
        check_in__year=date.today().year,
    ).count()
    return render(request, "member/attendance.html", {
        "records": records, "today_count": today_count, "month_count": month_count,
    })


@login_required
def my_progress(request):
    logs = ProgressLog.objects.filter(member=request.user)
    chart_labels = [l.logged_on.strftime("%b %d") for l in reversed(logs[:12])]
    chart_weight = [float(l.weight_kg) for l in reversed(logs[:12])]
    chart_bmi = [float(l.bmi) for l in reversed(logs[:12])]
    return render(request, "member/progress.html", {
        "logs": logs, "chart_labels": chart_labels,
        "chart_weight": chart_weight, "chart_bmi": chart_bmi,
    })


@login_required
def add_progress(request):
    if request.method == "POST":
        form = ProgressLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.member = request.user
            log.save()
            messages.success(request, "Progress logged.")
            return redirect("core:my_progress")
    else:
        form = ProgressLogForm()
    return render(request, "member/progress_form.html", {"form": form})


@login_required
def submit_testimonial(request):
    if request.method == "POST":
        form = TestimonialMemberForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.author_name = request.user.display_name
            t.author_role = "Spartan Member"
            t.submitted_by = request.user
            t.is_published = False
            t.save()
            messages.success(request, "Thanks! Your testimonial is awaiting approval.")
            return redirect("core:dashboard")
    else:
        form = TestimonialMemberForm()
    return render(request, "member/testimonial_form.html", {"form": form})


# ---------- ADMIN PANEL ----------

@admin_required
def admin_dashboard(request):
    today = date.today()
    revenue_month = Payment.objects.filter(
        status=Payment.Status.PAID, paid_on__month=today.month, paid_on__year=today.year
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    revenue_total = Payment.objects.filter(status=Payment.Status.PAID).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    member_count = User.objects.filter(role=User.Role.MEMBER).count()
    active_memberships = Membership.objects.filter(status=Membership.Status.ACTIVE, end_date__gte=today).count()
    expiring_soon = Membership.objects.filter(
        status=Membership.Status.ACTIVE, end_date__lte=today + timedelta(days=7), end_date__gte=today
    ).select_related("member", "plan")
    todays_attendance = Attendance.objects.filter(check_in__date=today).count()
    pending_messages = ContactMessage.objects.filter(handled=False).count()
    pending_testimonials = Testimonial.objects.filter(is_published=False).count()

    # Last 7 days revenue chart
    chart_labels, chart_data = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime("%a"))
        rev = Payment.objects.filter(
            status=Payment.Status.PAID, paid_on__date=d
        ).aggregate(total=Sum("amount"))["total"] or 0
        chart_data.append(float(rev))

    plan_breakdown = (
        Membership.objects.filter(status=Membership.Status.ACTIVE)
        .values("plan__name").annotate(c=Count("id")).order_by("-c")
    )

    recent_members = User.objects.filter(role=User.Role.MEMBER).order_by("-date_joined")[:5]
    recent_payments = Payment.objects.select_related("member")[:5]

    return render(request, "admin_panel/dashboard.html", {
        "revenue_month": revenue_month, "revenue_total": revenue_total,
        "member_count": member_count, "active_memberships": active_memberships,
        "expiring_soon": expiring_soon, "todays_attendance": todays_attendance,
        "pending_messages": pending_messages, "pending_testimonials": pending_testimonials,
        "chart_labels": chart_labels, "chart_data": chart_data,
        "plan_breakdown": list(plan_breakdown),
        "recent_members": recent_members, "recent_payments": recent_payments,
    })


# Members management

@admin_required
def member_list(request):
    q = request.GET.get("q", "").strip()
    members = User.objects.filter(role=User.Role.MEMBER)
    if q:
        members = members.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q)
            | Q(last_name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q)
        )
    return render(request, "admin_panel/members/list.html", {"members": members, "q": q})


@perm_required("can_add_member")
def member_add(request):
    if request.method == "POST":
        form = MemberCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Member {user.display_name} created.")
            return redirect("core:member_detail", pk=user.pk)
    else:
        form = MemberCreateForm()
    return render(request, "admin_panel/members/form.html", {"form": form, "title": "Add Member"})


@admin_required
def member_detail(request, pk):
    member = get_object_or_404(User, pk=pk, role=User.Role.MEMBER)
    memberships = Membership.objects.filter(member=member).select_related("plan")
    payments = Payment.objects.filter(member=member)[:10]
    attendance = Attendance.objects.filter(member=member)[:10]
    return render(request, "admin_panel/members/detail.html", {
        "member": member, "memberships": memberships,
        "payments": payments, "attendance": attendance,
    })


@perm_required("can_edit_member")
def member_edit(request, pk):
    member = get_object_or_404(User, pk=pk, role=User.Role.MEMBER)
    if request.method == "POST":
        form = MemberEditForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Member updated.")
            return redirect("core:member_detail", pk=member.pk)
    else:
        form = MemberEditForm(instance=member)
    return render(request, "admin_panel/members/form.html", {"form": form, "title": f"Edit {member.display_name}"})


@perm_required("can_delete_member")
def member_delete(request, pk):
    member = get_object_or_404(User, pk=pk, role=User.Role.MEMBER)
    if request.method == "POST":
        name = member.display_name
        member.delete()
        messages.success(request, f"Member {name} deleted.")
        return redirect("core:member_list")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": member, "title": "Delete Member", "back_url": reverse("core:member_list"),
    })


# Plans

@admin_required
def plan_list(request):
    plans_qs = Plan.objects.all()
    return render(request, "admin_panel/plans/list.html", {"plans": plans_qs})


@perm_required("can_manage_plans")
def plan_add(request):
    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Plan created.")
            return redirect("core:plan_list")
    else:
        form = PlanForm()
    return render(request, "admin_panel/plans/form.html", {"form": form, "title": "Add Plan"})


@perm_required("can_manage_plans")
def plan_edit(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == "POST":
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Plan updated.")
            return redirect("core:plan_list")
    else:
        form = PlanForm(instance=plan)
    return render(request, "admin_panel/plans/form.html", {"form": form, "title": f"Edit {plan.name}"})


@perm_required("can_manage_plans")
def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == "POST":
        plan.delete()
        messages.success(request, "Plan deleted.")
        return redirect("core:plan_list")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": plan, "title": "Delete Plan", "back_url": reverse("core:plan_list"),
    })


# Memberships

@admin_required
def membership_list(request):
    items = Membership.objects.select_related("member", "plan")[:200]
    return render(request, "admin_panel/memberships/list.html", {"items": items})


@perm_required("can_manage_payments")
def membership_add(request):
    if request.method == "POST":
        form = MembershipForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.created_by = request.user
            m.save()
            messages.success(request, "Membership added.")
            return redirect("core:membership_list")
    else:
        form = MembershipForm()
    return render(request, "admin_panel/memberships/form.html", {"form": form, "title": "Add Membership"})


@perm_required("can_manage_payments")
def membership_cancel(request, pk):
    m = get_object_or_404(Membership, pk=pk)
    m.status = Membership.Status.CANCELLED
    m.save()
    messages.success(request, "Membership cancelled.")
    return redirect("core:membership_list")


# Payments

@admin_required
def payment_list(request):
    items = Payment.objects.select_related("member", "membership__plan")[:200]
    total = items.aggregate(t=Sum("amount"))["t"] or 0
    return render(request, "admin_panel/payments/list.html", {"items": items, "total": total})


@perm_required("can_manage_payments")
def payment_add(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.recorded_by = request.user
            p.save()
            messages.success(request, "Payment recorded.")
            return redirect("core:payment_list")
    else:
        form = PaymentForm()
    return render(request, "admin_panel/payments/form.html", {"form": form, "title": "Record Payment"})


# Classes

@admin_required
def class_list(request):
    items = GymClass.objects.select_related("trainer")
    return render(request, "admin_panel/classes/list.html", {"items": items})


@perm_required("can_manage_classes")
def class_add(request):
    if request.method == "POST":
        form = GymClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class created.")
            return redirect("core:class_list")
    else:
        form = GymClassForm()
    return render(request, "admin_panel/classes/form.html", {"form": form, "title": "Add Class"})


@perm_required("can_manage_classes")
def class_edit(request, pk):
    item = get_object_or_404(GymClass, pk=pk)
    if request.method == "POST":
        form = GymClassForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Class updated.")
            return redirect("core:class_list")
    else:
        form = GymClassForm(instance=item)
    return render(request, "admin_panel/classes/form.html", {"form": form, "title": f"Edit {item.name}"})


@perm_required("can_manage_classes")
def class_delete(request, pk):
    item = get_object_or_404(GymClass, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Class deleted.")
        return redirect("core:class_list")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": item, "title": "Delete Class", "back_url": reverse("core:class_list"),
    })


# Trainers

@admin_required
def trainer_list(request):
    items = Trainer.objects.all()
    return render(request, "admin_panel/trainers/list.html", {"items": items})


@perm_required("can_manage_classes")
def trainer_add(request):
    if request.method == "POST":
        form = TrainerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer added.")
            return redirect("core:trainer_list")
    else:
        form = TrainerForm()
    return render(request, "admin_panel/trainers/form.html", {"form": form, "title": "Add Trainer"})


@perm_required("can_manage_classes")
def trainer_edit(request, pk):
    item = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        form = TrainerForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer updated.")
            return redirect("core:trainer_list")
    else:
        form = TrainerForm(instance=item)
    return render(request, "admin_panel/trainers/form.html", {"form": form, "title": f"Edit {item.name}"})


@perm_required("can_manage_classes")
def trainer_delete(request, pk):
    item = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Trainer deleted.")
        return redirect("core:trainer_list")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": item, "title": "Delete Trainer", "back_url": reverse("core:trainer_list"),
    })


# Testimonials

@admin_required
def testimonial_list(request):
    items = Testimonial.objects.all()
    return render(request, "admin_panel/testimonials/list.html", {"items": items})


@perm_required("can_manage_testimonials")
def testimonial_add(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial added.")
            return redirect("core:testimonial_list")
    else:
        form = TestimonialForm()
    return render(request, "admin_panel/testimonials/form.html", {"form": form, "title": "Add Testimonial"})


@perm_required("can_manage_testimonials")
def testimonial_edit(request, pk):
    item = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial updated.")
            return redirect("core:testimonial_list")
    else:
        form = TestimonialForm(instance=item)
    return render(request, "admin_panel/testimonials/form.html", {"form": form, "title": f"Edit {item.author_name}"})


@perm_required("can_manage_testimonials")
def testimonial_delete(request, pk):
    item = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Testimonial deleted.")
        return redirect("core:testimonial_list")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": item, "title": "Delete Testimonial", "back_url": reverse("core:testimonial_list"),
    })


# Attendance + Messages

@admin_required
def attendance_list(request):
    items = Attendance.objects.select_related("member")[:200]
    return render(request, "admin_panel/attendance/list.html", {"items": items})


@admin_required
def admin_check_in(request):
    if request.method == "POST":
        member_id = request.POST.get("member_id")
        try:
            member = User.objects.get(pk=member_id, role=User.Role.MEMBER)
            Attendance.objects.create(member=member, note="Front-desk check-in")
            messages.success(request, f"Checked in {member.display_name}.")
        except User.DoesNotExist:
            messages.error(request, "Member not found.")
        return redirect("core:attendance_list")
    members = User.objects.filter(role=User.Role.MEMBER, is_active=True)
    return render(request, "admin_panel/attendance/check_in.html", {"members": members})


@admin_required
def message_list(request):
    items = ContactMessage.objects.all()
    return render(request, "admin_panel/messages/list.html", {"items": items})


@admin_required
def message_handle(request, pk):
    item = get_object_or_404(ContactMessage, pk=pk)
    item.handled = not item.handled
    item.save()
    return redirect("core:message_list")


# Super-admin: staff

@super_admin_required
def staff_list(request):
    staff = User.objects.filter(role__in=[User.Role.SUPER_ADMIN, User.Role.ADMIN])
    return render(request, "admin_panel/staff/list.html", {"staff": staff})


@super_admin_required
def staff_add(request):
    if request.method == "POST":
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Staff {user.display_name} created.")
            return redirect("core:staff_list")
    else:
        form = AdminUserForm(initial={"role": User.Role.ADMIN, "is_active": True})
    return render(request, "admin_panel/staff/form.html", {"form": form, "title": "Add Staff"})


@super_admin_required
def staff_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff updated.")
            return redirect("core:staff_list")
    else:
        form = AdminUserForm(instance=user)
    return render(request, "admin_panel/staff/form.html", {"form": form, "title": f"Edit {user.display_name}"})


@super_admin_required
def staff_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You can't delete yourself.")
        return redirect("core:staff_list")
    if request.method == "POST":
        user.delete()
        messages.success(request, "Staff deleted.")
        return redirect("core:staff_list")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": user, "title": "Delete Staff", "back_url": reverse("core:staff_list"),
    })


@super_admin_required
def site_settings_edit(request):
    s = SiteSettings.load()
    if request.method == "POST":
        form = SiteSettingsForm(request.POST, instance=s)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings updated.")
            return redirect("core:site_settings")
    else:
        form = SiteSettingsForm(instance=s)
    return render(request, "admin_panel/site_settings.html", {"form": form})
