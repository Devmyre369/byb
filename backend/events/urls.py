'''
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
'''



from django.urls import path

from events.views import (
    EventListCreateView,
    EventDetailView,
    EventOrganiserListCreateView,
    EventOrganiserDetailView,
)


urlpatterns = [
    # Event listing and creation
    path(
        "",
        EventListCreateView.as_view(),
        name="event-list-create",
    ),

    # Individual event
    path(
        "<uuid:event_id>/",
        EventDetailView.as_view(),
        name="event-detail",
    ),

    # Event organiser listing and creation
    path(
        "<uuid:event_id>/organisers/",
        EventOrganiserListCreateView.as_view(),
        name="event-organiser-list-create",
    ),

    # Individual co-organiser management
    path(
        "<uuid:event_id>/organisers/<uuid:organiser_id>/",
        EventOrganiserDetailView.as_view(),
        name="event-organiser-detail",
    ),
]
