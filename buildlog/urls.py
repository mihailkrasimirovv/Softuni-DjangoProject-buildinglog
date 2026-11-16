"""Root URL configuration of the BuildLog project."""

from django.contrib import admin
from django.contrib.staticfiles.views import serve as serve_static
from django.urls import include, path, re_path

urlpatterns = [
    path("", include("common.urls")),
    path("sites/", include("sites.urls")),
    path("contractors/", include("contractors.urls")),
    path("activities/", include("works.urls")),
    path("inspections/", include("inspections.urls")),
    path("admin/", admin.site.urls),
    # The project is meant to be evaluated locally with DEBUG switched off
    # (so the custom 404 page is visible). Django's development server only
    # serves static files when DEBUG is on, therefore they are served
    # explicitly here. A real deployment would use a web server or WhiteNoise.
    re_path(r"^static/(?P<path>.*)$", serve_static, {"insecure": True}),
]
