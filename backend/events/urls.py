from django.urls import path

from events.views import (
    EventListCreateView,
    EventDetailView,
)


urlpatterns = [
    path(
        "",
        EventListCreateView.as_view(),
        name="event-list-create",
    ),
    path(
        "<uuid:event_id>/",
        EventDetailView.as_view(),
        name="event-detail",
    ),
]