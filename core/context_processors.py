"""Template context processors."""
from .models import SiteSettings


def site_settings(request):
    try:
        settings_obj = SiteSettings.load()
    except Exception:
        settings_obj = None
    return {"site": settings_obj}
