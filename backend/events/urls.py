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
'''


from django.urls import path

from events.views import (
    EventListCreateView,
    EventDetailView,
    EventOrganiserListCreateView,
    EventOrganiserDetailView,
    EventParticipantListCreateView,
    EventParticipantMeView,
    EventParticipantDetailView,
)


urlpatterns = [
    # Events
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

    # Event organisers
    path(
        "<uuid:event_id>/organisers/",
        EventOrganiserListCreateView.as_view(),
        name="event-organiser-list-create",
    ),
    path(
        "<uuid:event_id>/organisers/<uuid:organiser_id>/",
        EventOrganiserDetailView.as_view(),
        name="event-organiser-detail",
    ),

    # Event participants
    path(
        "<uuid:event_id>/participants/",
        EventParticipantListCreateView.as_view(),
        name="event-participant-list-create",
    ),
    path(
        "<uuid:event_id>/participants/me/respond/",
        EventParticipantMeView.as_view(),
        name="event-participant-respond",
    ),
    path(
        "<uuid:event_id>/participants/me/",
        EventParticipantMeView.as_view(),
        name="event-participant-me",
    ),
    path(
        "<uuid:event_id>/participants/<uuid:participant_id>/",
        EventParticipantDetailView.as_view(),
        name="event-participant-detail",
    ),
]
