"""API URL routes."""
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import api_views

app_name = "api"

urlpatterns = [
    path("plans/", api_views.public_plans, name="plans"),
    path("testimonials/", api_views.public_testimonials, name="testimonials"),
    path("classes/", api_views.public_classes, name="classes"),
    path("trainers/", api_views.public_trainers, name="trainers"),
    path("admin/summary/", api_views.admin_summary, name="admin_summary"),
    path("auth/token/", obtain_auth_token, name="token"),
]
