
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from events.models import Event, EventOrganiser


CO_ORGANISER_PERMISSIONS = {
    "can_edit_event",
    "can_manage_participants",
    "can_manage_registrations",
    "can_change_visibility",
    "can_moderate_media",
    "can_delete_event",
}


def _validate_permissions(permissions):
    if permissions is None:
        return {}

    if not isinstance(permissions, dict):
        raise ValidationError("Permissions must be provided as a dictionary.")

    invalid_fields = set(permissions.keys()) - CO_ORGANISER_PERMISSIONS

    if invalid_fields:
        raise ValidationError(
            f"Invalid permission fields: {', '.join(sorted(invalid_fields))}"
        )

    for field, value in permissions.items():
        if not isinstance(value, bool):
            raise ValidationError({
                field: "Permission values must be true or false."
            })

    return permissions


def _get_manageable_event(event):
    try:
        locked_event = Event.objects.select_for_update().get(pk=event.pk)
    except Event.DoesNotExist:
        raise ValidationError("Event does not exist.")

    if (
        locked_event.is_deleted
        or locked_event.status == Event.Status.ARCHIVED
        or locked_event.archived_at is not None
    ):
        raise ValidationError(
            "Organisers cannot be managed for deleted or archived events."
        )

    return locked_event


def _require_primary_organiser(actor, event):
    if not actor or not actor.is_authenticated:
        raise PermissionDenied("Authentication is required.")

    if actor.pk != event.creator_id:
        raise PermissionDenied(
            "Only the primary organiser can manage co-organisers."
        )


@transaction.atomic
def add_co_organiser(*, event, actor, user, permissions=None):
    locked_event = _get_manageable_event(event)

    _require_primary_organiser(actor, locked_event)

    if not user or not user.is_authenticated:
        raise ValidationError("A valid user must be provided.")

    if user.pk == locked_event.creator_id:
        raise ValidationError(
            "The event creator is already the primary organiser."
        )

    validated_permissions = _validate_permissions(permissions)

    if EventOrganiser.objects.filter(
        event=locked_event,
        user=user
    ).exists():
        raise ValidationError(
            "This user is already an organiser of the event."
        )

    organiser = EventOrganiser(
        event=locked_event,
        user=user,
        role=EventOrganiser.Role.CO_ORGANISER,
        **validated_permissions
    )

    organiser.full_clean()
    organiser.save()

    return organiser


@transaction.atomic
def update_co_organiser_permissions(
    *,
    event,
    actor,
    organiser_id,
    permissions
):
    locked_event = _get_manageable_event(event)

    _require_primary_organiser(actor, locked_event)

    validated_permissions = _validate_permissions(permissions)

    if not validated_permissions:
        raise ValidationError(
            "At least one permission must be provided."
        )

    try:
        organiser = EventOrganiser.objects.select_for_update().get(
            id=organiser_id,
            event=locked_event,
            role=EventOrganiser.Role.CO_ORGANISER
        )
    except EventOrganiser.DoesNotExist:
        raise ValidationError("Co-organiser not found.")

    for field, value in validated_permissions.items():
        setattr(organiser, field, value)

    organiser.full_clean()

    # EventOrganiser has added_at, not updated_at.
    organiser.save(update_fields=list(validated_permissions.keys()))

    return organiser


@transaction.atomic
def remove_co_organiser(*, event, actor, organiser_id):
    locked_event = _get_manageable_event(event)

    _require_primary_organiser(actor, locked_event)

    try:
        organiser = EventOrganiser.objects.select_for_update().get(
            id=organiser_id,
            event=locked_event,
            role=EventOrganiser.Role.CO_ORGANISER
        )
    except EventOrganiser.DoesNotExist:
        raise ValidationError("Co-organiser not found.")

    organiser.delete()

    return True
