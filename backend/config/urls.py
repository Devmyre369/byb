
from django.contrib import admin
from django.urls import include, path

from accounts.api_views import health_check


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/health/",
        health_check,
        name="health-check",
    ),

    path(
        "api/accounts/",
        include("accounts.urls"),
    ),

    path(
        "api/events/",
        include("events.urls"),
    ),
    path(
    "api/hubs/",
    include("hubs.urls"),
),
]