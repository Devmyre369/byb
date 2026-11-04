

''''from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from events.models import Event, EventOrganiser
from events.services.permissions import can_delete_event


EVENT_RETENTION_DAYS = 30


@transaction.atomic
def create_event(*, creator, event_data):
    """
    Create an event and automatically assign its creator
    as the primary organiser.

    Personal and Social events may be created retrospectively.
    Public events must have a future start date.
    """

    if not creator or not creator.is_authenticated:
        raise PermissionDenied("You must be logged in to create an event.")

    data = dict(event_data)

    # These fields are controlled by the service, not the client.
    data.pop("creator", None)
    data.pop("status", None)
    data.pop("completed_at", None)
    data.pop("archive_at", None)
    data.pop("archived_at", None)
    data.pop("is_deleted", None)
    data.pop("deleted_at", None)
    data.pop("deleted_by", None)

    event_type = data.get("event_type")
    starts_at = data.get("starts_at")
    ends_at = data.get("ends_at")

    if not event_type or not starts_at:
        raise ValidationError(
            "Event type and start date/time are required."
        )

    now = timezone.now()

    # Public events cannot be created retrospectively.
    if event_type == "PUBLIC" and starts_at <= now:
        raise ValidationError(
            "Public events must have a future start date and time."
        )

    event = Event(
        creator=creator,
        **data,
    )

    # Determine the initial lifecycle status.
    if starts_at > now:
        event.status = "UPCOMING"

    elif ends_at and ends_at > now:
        event.status = "ONGOING"

    else:
        event.status = "COMPLETED"
        event.completed_at = now
        event.archive_at = now + timedelta(
            days=EVENT_RETENTION_DAYS
        )

    event.full_clean()
    event.save()

    # Every event creator is its primary organiser.
    primary_organiser = EventOrganiser(
        event=event,
        user=creator,
        role="PRIMARY",
    )

    primary_organiser.full_clean()
    primary_organiser.save()

    return event


@transaction.atomic
def soft_delete_event(*, event, user):
    """
    Soft-delete an event if the user has permission.

    The event and its media are not permanently deleted.
    """

    # Lock the event row to avoid concurrent deletion updates.
    event = Event.objects.select_for_update().get(pk=event.pk)

    if event.is_deleted:
        return event

    if not can_delete_event(user, event):
        raise PermissionDenied(
            "You do not have permission to delete this event."
        )

    event.is_deleted = True
    event.deleted_at = timezone.now()
    event.deleted_by = user

    event.full_clean()
    event.save(
        update_fields=[
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "updated_at",
        ]
    )

    return event
    '''

from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from events.models import Event, EventOrganiser
from events.services.permissions import can_delete_event


EVENT_RETENTION_DAYS = 30


@transaction.atomic
def create_event(*, creator, event_data):
    """
    Create an event and automatically assign its creator
    as the primary organiser.
    """

    if not creator or not creator.is_authenticated:
        raise PermissionDenied(
            "You must be logged in to create an event."
        )

    data = dict(event_data)

    # These fields are managed by the service.
    protected_fields = (
        "creator",
        "status",
        "completed_at",
        "archive_at",
        "archived_at",
        "is_deleted",
        "deleted_at",
        "deleted_by",
    )

    for field in protected_fields:
        data.pop(field, None)

    event_type = data.get("event_type")
    starts_at = data.get("starts_at")
    ends_at = data.get("ends_at")

    if not event_type or not starts_at:
        raise ValidationError(
            "Event type and start date/time are required."
        )

    now = timezone.now()

    if (
        event_type == Event.EventType.PUBLIC
        and starts_at <= now
    ):
        raise ValidationError(
            "Public events must have a future start date and time."
        )

    event = Event(
        creator=creator,
        **data,
    )

    if starts_at > now:
        event.status = Event.Status.UPCOMING

    elif ends_at and ends_at > now:
        event.status = Event.Status.ONGOING

    else:
        event.status = Event.Status.COMPLETED
        event.completed_at = now
        event.archive_at = now + timedelta(
            days=EVENT_RETENTION_DAYS
        )

    event.full_clean()
    event.save()

    primary_organiser = EventOrganiser(
        event=event,
        user=creator,
        role=EventOrganiser.Role.PRIMARY,
    )

    primary_organiser.full_clean()
    primary_organiser.save()

    return event


@transaction.atomic
def soft_delete_event(*, event, user):
    """
    Soft-delete an event when the user has permission.
    """

    event = Event.objects.select_for_update().get(
        pk=event.pk
    )

    if event.is_deleted:
        return event

    if not can_delete_event(user, event):
        raise PermissionDenied(
            "You do not have permission to delete this event."
        )

    event.is_deleted = True
    event.deleted_at = timezone.now()
    event.deleted_by = user

    event.full_clean()

    event.save(
        update_fields=[
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "updated_at",
        ]
    )

    return event