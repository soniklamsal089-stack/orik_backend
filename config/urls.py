from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    """Cheap liveness probe for the host/uptime checks."""
    return JsonResponse({"status": "ok"})


def root(_request):
    """Root endpoint showing API is live."""
    return JsonResponse({
        "message": "ORIK Webcraft API",
        "status": "running",
        "endpoints": {
            "admin": "/admin/",
            "api_content": "/api/content/",
            "api_enquiries": "/api/enquiries/",
            "health": "/api/health/"
        }
    })


urlpatterns = [
    path("", root, name="root"),
    path("admin/", admin.site.urls),
    path("api/", include("enquiries.urls")),
    path("api/", include("content.urls")),
    path("api/health/", health, name="health"),
]

# Serve media files in both development and production
# In production, Whitenoise will handle this efficiently
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Additional debug toolbar or other dev-only routes can go here
    pass
