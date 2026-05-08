"""Core URL routes."""
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # Public
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("plans/", views.plans, name="plans"),
    path("classes/", views.classes_public, name="classes"),
    path("trainers/", views.trainers_public, name="trainers"),
    path("contact/", views.contact, name="contact"),

    # Authenticated dashboard router
    path("dashboard/", views.dashboard, name="dashboard"),

    # Member portal
    path("me/membership/", views.my_membership, name="my_membership"),
    path("me/membership/subscribe/<int:plan_id>/", views.subscribe_plan, name="subscribe"),
    path("me/classes/", views.my_classes, name="my_classes"),
    path("me/classes/book/<int:class_id>/", views.book_class, name="book_class"),
    path("me/classes/cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("me/check-in/", views.member_check_in, name="check_in"),
    path("me/attendance/", views.my_attendance, name="my_attendance"),
    path("me/progress/", views.my_progress, name="my_progress"),
    path("me/progress/add/", views.add_progress, name="add_progress"),
    path("me/testimonial/", views.submit_testimonial, name="submit_testimonial"),

    # Admin section
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),

    path("admin-panel/members/", views.member_list, name="member_list"),
    path("admin-panel/members/add/", views.member_add, name="member_add"),
    path("admin-panel/members/<int:pk>/", views.member_detail, name="member_detail"),
    path("admin-panel/members/<int:pk>/edit/", views.member_edit, name="member_edit"),
    path("admin-panel/members/<int:pk>/delete/", views.member_delete, name="member_delete"),

    path("admin-panel/plans/", views.plan_list, name="plan_list"),
    path("admin-panel/plans/add/", views.plan_add, name="plan_add"),
    path("admin-panel/plans/<int:pk>/edit/", views.plan_edit, name="plan_edit"),
    path("admin-panel/plans/<int:pk>/delete/", views.plan_delete, name="plan_delete"),

    path("admin-panel/memberships/", views.membership_list, name="membership_list"),
    path("admin-panel/memberships/add/", views.membership_add, name="membership_add"),
    path("admin-panel/memberships/<int:pk>/cancel/", views.membership_cancel, name="membership_cancel"),

    path("admin-panel/payments/", views.payment_list, name="payment_list"),
    path("admin-panel/payments/add/", views.payment_add, name="payment_add"),

    path("admin-panel/classes/", views.class_list, name="class_list"),
    path("admin-panel/classes/add/", views.class_add, name="class_add"),
    path("admin-panel/classes/<int:pk>/edit/", views.class_edit, name="class_edit"),
    path("admin-panel/classes/<int:pk>/delete/", views.class_delete, name="class_delete"),

    path("admin-panel/trainers/", views.trainer_list, name="trainer_list"),
    path("admin-panel/trainers/add/", views.trainer_add, name="trainer_add"),
    path("admin-panel/trainers/<int:pk>/edit/", views.trainer_edit, name="trainer_edit"),
    path("admin-panel/trainers/<int:pk>/delete/", views.trainer_delete, name="trainer_delete"),

    path("admin-panel/testimonials/", views.testimonial_list, name="testimonial_list"),
    path("admin-panel/testimonials/add/", views.testimonial_add, name="testimonial_add"),
    path("admin-panel/testimonials/<int:pk>/edit/", views.testimonial_edit, name="testimonial_edit"),
    path("admin-panel/testimonials/<int:pk>/delete/", views.testimonial_delete, name="testimonial_delete"),

    path("admin-panel/attendance/", views.attendance_list, name="attendance_list"),
    path("admin-panel/attendance/check-in/", views.admin_check_in, name="admin_check_in"),
    path("admin-panel/messages/", views.message_list, name="message_list"),
    path("admin-panel/messages/<int:pk>/handle/", views.message_handle, name="message_handle"),

    # Super-admin
    path("admin-panel/staff/", views.staff_list, name="staff_list"),
    path("admin-panel/staff/add/", views.staff_add, name="staff_add"),
    path("admin-panel/staff/<int:pk>/edit/", views.staff_edit, name="staff_edit"),
    path("admin-panel/staff/<int:pk>/delete/", views.staff_delete, name="staff_delete"),
    path("admin-panel/site-settings/", views.site_settings_edit, name="site_settings"),
]
