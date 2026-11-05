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
    '''


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
