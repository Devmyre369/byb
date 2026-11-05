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


def _is_event_organiser(user, event):
    if not _is_authenticated(user):
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
    ).exists()


def _is_explicit_participant(user, event):
    if not _is_authenticated(user):
        return False

    participant = EventParticipant.objects.filter(
        event=event,
        user=user,
    ).first()

    if not participant:
        return False

    # Social event access requires accepted participation.
    if event.event_type == "SOCIAL":
        return participant.status == "ACCEPTED"

    # Personal events can explicitly authorise invitees
    # and contributors.
    if event.event_type == "PERSONAL":
        return participant.status in ("INVITED", "ACCEPTED")

    return False


def _has_confirmed_registration(user, event):
    if not _is_authenticated(user):
        return False

    return EventRegistration.objects.filter(
        event=event,
        user=user,
        status="CONFIRMED",
    ).exists()


def can_view_event(user, event):
    """
    Determine whether a user can view an event.

    Before archival:
    - Public events follow their visibility setting.
    - Private and selected-audience events require explicit access.

    After archival:
    - Only the creator, organisers, eligible participants,
      and confirmed public-event attendees can view the event.

    Deleted events are not accessible through this function.
    """

    if not _is_authenticated(user):
        return False

    if event.is_deleted:
        return False

    if _is_event_creator(user, event):
        return True

    if _is_event_organiser(user, event):
        return True

    # Archived events are restricted to eligible participants.
    if event.status == "ARCHIVED":
        return (
            _is_explicit_participant(user, event)
            or _has_confirmed_registration(user, event)
        )

    # Public visibility allows authenticated BYB users to view.
    if event.visibility == "PUBLIC":
        return True

    # Private and selected-audience events require explicit access.
    return _is_explicit_participant(user, event)


def can_discover_event(user, event):
    """
    Determine whether an event can appear in public discovery.

    Only non-deleted, non-archived public events are discoverable.
    """

    if not _is_authenticated(user):
        return False

    return (
        not event.is_deleted
        and event.status != "ARCHIVED"
        and event.visibility == "PUBLIC"
    )
    

from events.models import (
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


def _is_event_organiser(user, event):
    if not _is_authenticated(user):
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
    ).exists()


def _is_explicit_participant(user, event):
    if not _is_authenticated(user):
        return False

    participant = EventParticipant.objects.filter(
        event=event,
        user=user,
    ).first()

    if not participant:
        return False

    if event.event_type == "SOCIAL":
        return participant.status == "ACCEPTED"

    if event.event_type == "PERSONAL":
        return participant.status in ("INVITED", "ACCEPTED")

    return False


def _has_confirmed_registration(user, event):
    if not _is_authenticated(user):
        return False

    return EventRegistration.objects.filter(
        event=event,
        user=user,
        status="CONFIRMED",
    ).exists()


def _has_event_access(user, event):
    if _is_event_creator(user, event):
        return True

    if _is_event_organiser(user, event):
        return True

    if event.event_type == "PUBLIC":
        return _has_confirmed_registration(user, event)

    return _is_explicit_participant(user, event)


def can_view_event(user, event):
    """
    Check whether a user can view an event.

    Deleted events are never accessible.

    Archived events are restricted to the creator,
    organisers, and eligible participants or attendees.

    Before archival:
    - PUBLIC visibility allows authenticated BYB users.
    - SELECTED visibility requires explicit participation
      or a confirmed public-event registration.
    - PRIVATE visibility requires creator or organiser access.
    """

    if not _is_authenticated(user):
        return False

    if event.is_deleted:
        return False

    if event.status == "ARCHIVED":
        return _has_event_access(user, event)

    if _is_event_creator(user, event):
        return True

    if _is_event_organiser(user, event):
        return True

    if event.visibility == "PUBLIC":
        return True

    if event.visibility == "SELECTED":
        return _has_event_access(user, event)

    return False


def can_discover_event(user, event):
    """
    Check whether an event can appear in public discovery.
    """

    if not _is_authenticated(user):
        return False

    return (
        not event.is_deleted
        and event.status != "ARCHIVED"
        and event.visibility == "PUBLIC"
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


def _is_event_organiser(user, event):
    if not _is_authenticated(user):
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
    ).exists()


def _is_explicit_participant(user, event):
    if not _is_authenticated(user):
        return False

    participant = EventParticipant.objects.filter(
        event=event,
        user=user,
    ).first()

    if not participant:
        return False

    if event.event_type == Event.EventType.SOCIAL:
        return participant.status == EventParticipant.Status.ACCEPTED

    if event.event_type == Event.EventType.PERSONAL:
        return participant.status in (
            EventParticipant.Status.INVITED,
            EventParticipant.Status.ACCEPTED,
        )

    return False


def _has_confirmed_registration(user, event):
    if not _is_authenticated(user):
        return False

    return EventRegistration.objects.filter(
        event=event,
        user=user,
        status=EventRegistration.Status.CONFIRMED,
    ).exists()


def _has_event_access(user, event):
    if _is_event_creator(user, event):
        return True

    if _is_event_organiser(user, event):
        return True

    if event.event_type == Event.EventType.PUBLIC:
        return _has_confirmed_registration(user, event)

    return _is_explicit_participant(user, event)


def can_view_event(user, event):
    """
    Check whether a user can view an event.

    Deleted events are inaccessible.

    Archived events are restricted to the creator,
    organisers, and eligible participants or attendees.

    Before archival:
    - PUBLIC visibility allows authenticated BYB users.
    - SELECTED visibility requires explicit participation
      or confirmed registration.
    - PRIVATE visibility requires explicit access.
    """

    if not _is_authenticated(user):
        return False

    if event.is_deleted:
        return False

    if event.status == Event.Status.ARCHIVED:
        return _has_event_access(user, event)

    if _is_event_creator(user, event):
        return True

    if _is_event_organiser(user, event):
        return True

    if event.visibility == Event.Visibility.PUBLIC:
        return True

    if event.visibility == Event.Visibility.SELECTED:
        return _has_event_access(user, event)

    return False


def can_discover_event(user, event):
    """
    Check whether an event can appear in public discovery.
    """

    if not _is_authenticated(user):
        return False

    return (
        not event.is_deleted
        and event.status != Event.Status.ARCHIVED
        and event.visibility == Event.Visibility.PUBLIC
    )


'''

from django.db.models import Exists, OuterRef, Q

from events.models import (
    Event,
    EventOrganiser,
    EventParticipant,
    EventRegistration,
)


def _is_authenticated(user):
    return bool(user and user.is_authenticated)


def _is_event_creator(user, event):
    return _is_authenticated(user) and event.creator_id == user.pk


def _is_event_organiser(user, event):
    if not _is_authenticated(user):
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
    ).exists()


def _is_explicit_participant(user, event):
    if not _is_authenticated(user):
        return False

    participant = EventParticipant.objects.filter(
        event=event,
        user=user,
    )

    if event.event_type == Event.EventType.SOCIAL:
        return participant.filter(
            status=EventParticipant.Status.ACCEPTED
        ).exists()

    if event.event_type == Event.EventType.PERSONAL:
        return participant.filter(
            status__in=[
                EventParticipant.Status.INVITED,
                EventParticipant.Status.ACCEPTED,
            ]
        ).exists()

    return False


def _has_confirmed_registration(user, event):
    if not _is_authenticated(user):
        return False

    return EventRegistration.objects.filter(
        event=event,
        user=user,
        status=EventRegistration.Status.CONFIRMED,
    ).exists()


def _has_event_access(user, event):
    return (
        _is_event_creator(user, event)
        or _is_event_organiser(user, event)
        or _is_explicit_participant(user, event)
        or _has_confirmed_registration(user, event)
    )


def can_view_event(user, event):
    if not _is_authenticated(user):
        return False

    if event.is_deleted:
        return False

    if _is_event_creator(user, event) or _is_event_organiser(user, event):
        return True

    if event.status == Event.Status.ARCHIVED:
        return (
            _is_explicit_participant(user, event)
            or _has_confirmed_registration(user, event)
        )

    if event.visibility == Event.Visibility.PUBLIC:
        return True

    if event.visibility == Event.Visibility.SELECTED:
        return (
            _is_explicit_participant(user, event)
            or (
                event.event_type == Event.EventType.PUBLIC
                and _has_confirmed_registration(user, event)
            )
        )

    return False


def get_accessible_events_queryset(user):
    if not _is_authenticated(user):
        return Event.objects.none()

    organiser_access = EventOrganiser.objects.filter(
        event_id=OuterRef("pk"),
        user_id=user.pk,
    )

    participant_access = EventParticipant.objects.filter(
        event_id=OuterRef("pk"),
        user_id=user.pk,
    ).filter(
        Q(
            event__event_type=Event.EventType.SOCIAL,
            status=EventParticipant.Status.ACCEPTED,
        )
        | Q(
            event__event_type=Event.EventType.PERSONAL,
            status__in=[
                EventParticipant.Status.INVITED,
                EventParticipant.Status.ACCEPTED,
            ],
        )
    )

    registration_access = EventRegistration.objects.filter(
        event_id=OuterRef("pk"),
        user_id=user.pk,
        status=EventRegistration.Status.CONFIRMED,
    )

    return (
        Event.objects.filter(is_deleted=False)
        .annotate(
            _user_is_organiser=Exists(organiser_access),
            _user_is_participant=Exists(participant_access),
            _user_is_registered=Exists(registration_access),
        )
        .filter(
            Q(creator_id=user.pk)
            | Q(_user_is_organiser=True)
            | (
                ~Q(status=Event.Status.ARCHIVED)
                & Q(visibility=Event.Visibility.PUBLIC)
            )
            | (
                Q(status=Event.Status.ARCHIVED)
                & (
                    Q(_user_is_participant=True)
                    | Q(_user_is_registered=True)
                )
            )
            | (
                ~Q(status=Event.Status.ARCHIVED)
                & Q(visibility=Event.Visibility.SELECTED)
                & (
                    Q(_user_is_participant=True)
                    | (
                        Q(event_type=Event.EventType.PUBLIC)
                        & Q(_user_is_registered=True)
                    )
                )
            )
        )
        .distinct()
    )


def can_discover_event(user, event):
    if not _is_authenticated(user):
        return False

    return (
        not event.is_deleted
        and event.status != Event.Status.ARCHIVED
        and event.visibility == Event.Visibility.PUBLIC
    )