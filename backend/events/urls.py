
from django.urls import path

from events.media_moderation_views import EventMediaModerationView

from events.media_views import (
    EventCoverImageUploadView,
    EventMediaUploadView,
    MomentsFeedView,
)

from events.views import (
    EventListCreateView,
    EventDetailView,
    EventOrganiserListCreateView,
    EventOrganiserDetailView,
    EventParticipantListCreateView,
    EventParticipantMeView,
    EventParticipantDetailView,
    EventRegistrationListCreateView,
    EventRegistrationMeView,
    EventRegistrationDetailView,
)


urlpatterns = [
    # Events
    path(
        "",
        EventListCreateView.as_view(),
        name="event-list-create",
    ),

    # Home - Vibes & Moments feed
    path(
        "moments/",
        MomentsFeedView.as_view(),
        name="moments-feed",
    ),

    path(
        "<uuid:event_id>/",
        EventDetailView.as_view(),
        name="event-detail",
    ),

    # Event cover image upload
    path(
        "cover-image/",
        EventCoverImageUploadView.as_view(),
        name="event-cover-image-upload",
    ),

    # Organisers
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

    # Participants
    path(
        "<uuid:event_id>/participants/",
        EventParticipantListCreateView.as_view(),
        name="event-participant-list-create",
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

    # Registrations
    path(
        "<uuid:event_id>/registrations/",
        EventRegistrationListCreateView.as_view(),
        name="event-registration-list-create",
    ),
    path(
        "<uuid:event_id>/registrations/me/",
        EventRegistrationMeView.as_view(),
        name="event-registration-me",
    ),
    path(
        "<uuid:event_id>/registrations/<uuid:registration_id>/",
        EventRegistrationDetailView.as_view(),
        name="event-registration-detail",
    ),

    # Event gallery media
    path(
        "<uuid:event_id>/media/",
        EventMediaUploadView.as_view(),
        name="event-media-upload",
    ),
    path(
        "<uuid:event_id>/media/<uuid:media_id>/moderate/",
        EventMediaModerationView.as_view(),
        name="event-media-moderate",
    ),
]
