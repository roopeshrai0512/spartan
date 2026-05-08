"""Spartan Gym - root URL configuration."""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse
from django.urls import path, include
from django.views.generic.base import RedirectView


def healthz(_request):
    return JsonResponse({"ok": True, "service": "spartan-gym"})


urlpatterns = [
    path("healthz", healthz),
    path("favicon.ico", RedirectView.as_view(url="/static/img/favicon.svg", permanent=True)),
    path("django-admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("api/", include("core.api_urls", namespace="api")),
    path("", include("core.urls", namespace="core")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Spartan Gym Administration"
admin.site.site_title = "Spartan Gym Admin"
admin.site.index_title = "Welcome to Spartan Gym Control Panel"
