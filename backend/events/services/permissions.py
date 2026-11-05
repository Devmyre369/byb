'''
from events.models import Event, EventOrganiser


def _is_authenticated(user):
    return bool(
        user
        and getattr(user, "is_authenticated", False)
    )


def _is_event_creator(user, event):
    return (
        _is_authenticated(user)
        and user.pk == event.creator_id
    )


def _has_co_organiser_permission(user, event, permission):
    if not _is_authenticated(user):
        return False

    if event.is_deleted:
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
        role=EventOrganiser.Role.CO_ORGANISER,
        **{permission: True}
    ).exists()


def can_delete_event(user, event):
    """
    The event creator can always delete their event.

    A co-organiser can delete it only when the creator
    has explicitly granted can_delete_event.
    """

    if not _is_authenticated(user) or event.is_deleted:
        return False

    if _is_event_creator(user, event):
        return True

    return _has_co_organiser_permission(
        user,
        event,
        "can_delete_event"
    )


def can_edit_event(user, event):
    """Check whether the user can edit event details."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_edit_event"
    )


def can_manage_participants(user, event):
    """Check whether the user can manage event participants."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_manage_participants"
    )


def can_manage_registrations(user, event):
    """Check whether the user can manage public event registrations."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_manage_registrations"
    )


def can_change_visibility(user, event):
    """Check whether the user can change event visibility."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_change_visibility"
    )


def can_moderate_media(user, event):
    """Check whether the user can moderate event media."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_moderate_media"
    )



from events.models import EventOrganiser


def _is_authenticated(user):
    return bool(
        user
        and getattr(user, "is_authenticated", False)
    )


def _is_event_creator(user, event):
    return (
        _is_authenticated(user)
        and user.pk == event.creator_id
    )


def _has_co_organiser_permission(user, event, permission):
    if not _is_authenticated(user) or event.is_deleted:
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
        role=EventOrganiser.Role.CO_ORGANISER,
        **{permission: True}
    ).exists()


def can_delete_event(user, event):
    if not _is_authenticated(user) or event.is_deleted:
        return False

    if _is_event_creator(user, event):
        return True

    return _has_co_organiser_permission(
        user, event, "can_delete_event"
    )


def can_edit_event(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_edit_event"
    )


def can_manage_participants(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_manage_participants"
    )


def can_manage_registrations(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_manage_registrations"
    )


def can_change_visibility(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_change_visibility"
    )


def can_moderate_media(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_moderate_media"
    )
    


from events.models import EventOrganiser


def _is_authenticated(user):
    return bool(
        user
        and getattr(user, "is_authenticated", False)
    )


def _is_event_creator(user, event):
    return (
        _is_authenticated(user)
        and user.pk == event.creator_id
    )


def _has_co_organiser_permission(user, event, permission):
    if not _is_authenticated(user) or event.is_deleted:
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
        role=EventOrganiser.Role.CO_ORGANISER,
        **{permission: True}
    ).exists()


def can_delete_event(user, event):
    if not _is_authenticated(user) or event.is_deleted:
        return False

    if _is_event_creator(user, event):
        return True

    return _has_co_organiser_permission(
        user, event, "can_delete_event"
    )


def can_edit_event(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_edit_event"
    )


def can_manage_participants(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_manage_participants"
    )


def can_manage_registrations(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_manage_registrations"
    )


def can_change_visibility(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_change_visibility"
    )


def can_moderate_media(user, event):
    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user, event, "can_moderate_media"
    )



from events.models import (
    Event,
    EventOrganiser,
    EventParticipant,
    EventRegistration,
)


def _is_authenticated(user):
    return bool(
        user
        and getattr(user, "is_authenticated", False)
    )


def _is_event_creator(user, event):
    return (
        _is_authenticated(user)
        and user.pk == event.creator_id
    )


def _has_co_organiser_permission(user, event, permission):
    if not _is_authenticated(user) or event.is_deleted:
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
        role=EventOrganiser.Role.CO_ORGANISER,
        **{permission: True}
    ).exists()


def can_delete_event(user, event):
    """
    The creator can delete their event.

    A co-organiser can delete it only when explicitly authorised.
    """

    if not _is_authenticated(user) or event.is_deleted:
        return False

    if _is_event_creator(user, event):
        return True

    return _has_co_organiser_permission(
        user,
        event,
        "can_delete_event",
    )


def can_edit_event(user, event):
    """Check whether the user can edit event details."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_edit_event",
    )


def can_manage_participants(user, event):
    """Check whether the user can manage event participants."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_manage_participants",
    )


def can_manage_registrations(user, event):
    """Check whether the user can manage public registrations."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_manage_registrations",
    )


def can_change_visibility(user, event):
    """Check whether the user can change event visibility."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_change_visibility",
    )


def can_moderate_media(user, event):
    """Check whether the user can moderate event media."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_moderate_media",
    )


def can_upload_event_media(user, event):
    """
    Check whether a user can upload images to an event.

    Personal:
        Creator and explicitly authorised contributors.

    Social:
        Accepted participants.

    Public:
        Confirmed attendees.

    Organisers:
        Creator and co-organisers with media moderation permission.

    Archived and deleted events do not accept new uploads.
    """

    if not _is_authenticated(user):
        return False

    if event.is_deleted:
        return False

    if event.status == Event.Status.ARCHIVED:
        return False

    # The event creator can upload to their own event.
    if _is_event_creator(user, event):
        return True

    # Co-organisers need explicit media moderation permission.
    if _has_co_organiser_permission(
        user,
        event,
        "can_moderate_media",
    ):
        return True

    # Personal events require explicit upload authorisation.
    if event.event_type == Event.EventType.PERSONAL:
        return EventParticipant.objects.filter(
            event=event,
            user=user,
            status__in=[
                EventParticipant.Status.INVITED,
                EventParticipant.Status.ACCEPTED,
            ],
            can_upload_media=True,
        ).exists()

    # Accepted Social participants can contribute images.
    if event.event_type == Event.EventType.SOCIAL:
        return EventParticipant.objects.filter(
            event=event,
            user=user,
            status=EventParticipant.Status.ACCEPTED,
        ).exists()

    # Public events require a confirmed registration.
    if event.event_type == Event.EventType.PUBLIC:
        return EventRegistration.objects.filter(
            event=event,
            user=user,
            status=EventRegistration.Status.CONFIRMED,
        ).exists()

    return False
'''


from events.models import (
    Event,
    EventOrganiser,
    EventParticipant,
    EventRegistration,
)


def _is_authenticated(user):
    return bool(
        user
        and getattr(user, "is_authenticated", False)
    )


def _is_event_creator(user, event):
    return (
        _is_authenticated(user)
        and user.pk == event.creator_id
    )


def _has_co_organiser_permission(user, event, permission):
    if not _is_authenticated(user) or event.is_deleted:
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
        role=EventOrganiser.Role.CO_ORGANISER,
        **{permission: True}
    ).exists()


def can_delete_event(user, event):
    """
    The creator can delete their event.

    A co-organiser can delete it only when explicitly authorised.
    """

    if not _is_authenticated(user) or event.is_deleted:
        return False

    if _is_event_creator(user, event):
        return True

    return _has_co_organiser_permission(
        user,
        event,
        "can_delete_event",
    )


def can_edit_event(user, event):
    """Check whether the user can edit event details."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_edit_event",
    )


def can_manage_participants(user, event):
    """Check whether the user can manage event participants."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_manage_participants",
    )


def can_manage_registrations(user, event):
    """Check whether the user can manage public registrations."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_manage_registrations",
    )


def can_change_visibility(user, event):
    """Check whether the user can change event visibility."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_change_visibility",
    )


def can_moderate_media(user, event):
    """Check whether the user can moderate event media."""

    if _is_event_creator(user, event):
        return not event.is_deleted

    return _has_co_organiser_permission(
        user,
        event,
        "can_moderate_media",
    )


def can_upload_event_media(user, event):
    """
    Check whether a user can upload images to an event.

    Personal:
        Creator and explicitly authorised contributors.

    Social:
        Accepted participants.

    Public:
        Confirmed attendees.

    Organisers:
        Creator and co-organisers with media moderation permission.

    Archived and deleted events do not accept new uploads.
    """

    if not _is_authenticated(user):
        return False

    if event.is_deleted:
        return False

    if event.status == Event.Status.ARCHIVED:
        return False

    # The event creator can upload to their own event.
    if _is_event_creator(user, event):
        return True

    # Co-organisers need explicit media moderation permission.
    if _has_co_organiser_permission(
        user,
        event,
        "can_moderate_media",
    ):
        return True

    # Personal events require explicit upload authorisation.
    if event.event_type == Event.EventType.PERSONAL:
        return EventParticipant.objects.filter(
            event=event,
            user=user,
            status__in=[
                EventParticipant.Status.INVITED,
                EventParticipant.Status.ACCEPTED,
            ],
            can_upload_media=True,
        ).exists()

    # Accepted Social participants can contribute images.
    if event.event_type == Event.EventType.SOCIAL:
        return EventParticipant.objects.filter(
            event=event,
            user=user,
            status=EventParticipant.Status.ACCEPTED,
        ).exists()

    # Public events require a confirmed registration.
    if event.event_type == Event.EventType.PUBLIC:
        return EventRegistration.objects.filter(
            event=event,
            user=user,
            status=EventRegistration.Status.CONFIRMED,
        ).exists()

    return False
