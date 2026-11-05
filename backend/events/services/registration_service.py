
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from events.models import Event, EventOrganiser, EventRegistration
from events.services.permissions import can_manage_registrations


def _require_authenticated(user):
    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication is required.")


def _get_locked_event(event):
    """
    Lock the event row so concurrent registration and approval
    operations cannot exceed its capacity.
    """
    event_id = getattr(event, "pk", event)

    try:
        return Event.objects.select_for_update().get(pk=event_id)
    except Event.DoesNotExist:
        raise ValidationError("Event does not exist.")


def _require_public_event(event):
    if event.event_type != Event.EventType.PUBLIC:
        raise ValidationError(
            "Only public events support event registration."
        )


def _require_active_event(event):
    if event.is_deleted:
        raise ValidationError("This event is no longer available.")

    if event.status in (
        Event.Status.COMPLETED,
        Event.Status.ARCHIVED,
    ):
        raise ValidationError(
            "Registrations are not available for completed or archived events."
        )


def _require_registration_open(event):
    now = timezone.now()

    if not event.registration_enabled:
        raise ValidationError(
            "Registration is currently disabled for this event."
        )

    if event.registration_opens_at and now < event.registration_opens_at:
        raise ValidationError(
            "Registration has not opened yet."
        )

    # If no closing time is specified, registration closes when
    # the event starts.
    closes_at = event.registration_closes_at or event.starts_at

    if now >= closes_at:
        raise ValidationError(
            "The registration window for this event has closed."
        )


def _require_registration_manager(actor, event):
    _require_authenticated(actor)

    if not can_manage_registrations(actor, event):
        raise PermissionDenied(
            "You do not have permission to manage registrations."
        )


def _require_not_organiser(event, user):
    is_organiser = EventOrganiser.objects.filter(
        event=event,
        user=user,
    ).exists()

    if is_organiser:
        raise ValidationError(
            "Event organisers cannot register as attendees."
        )


def _require_available_capacity(event):
    if event.capacity is None:
        return

    confirmed_count = EventRegistration.objects.filter(
        event=event,
        status=EventRegistration.Status.CONFIRMED,
    ).count()

    if confirmed_count >= event.capacity:
        raise ValidationError(
            "This event has reached its registration capacity."
        )


def _get_registration(event, registration_id):
    try:
        return EventRegistration.objects.select_for_update().get(
            event=event,
            pk=registration_id,
        )
    except EventRegistration.DoesNotExist:
        raise ValidationError("Registration not found.")


def _save_registration(registration):
    registration.full_clean()
    registration.save()
    return registration


@transaction.atomic
def register_for_event(*, event, user):
    """
    Register a user for a public event.

    AUTOMATIC mode:
        Registration is immediately CONFIRMED.

    APPROVAL mode:
        Registration is created as PENDING.
    """
    _require_authenticated(user)

    event = _get_locked_event(event)

    _require_public_event(event)
    _require_active_event(event)
    _require_registration_open(event)
    _require_not_organiser(event, user)

    registration = EventRegistration.objects.filter(
        event=event,
        user=user,
    ).first()

    if registration:
        if registration.status == EventRegistration.Status.CONFIRMED:
            raise ValidationError(
                "You are already registered for this event."
            )

        if registration.status == EventRegistration.Status.PENDING:
            raise ValidationError(
                "Your registration is already awaiting approval."
            )

        if registration.status == EventRegistration.Status.REJECTED:
            raise ValidationError(
                "Your registration was rejected and cannot be resubmitted."
            )

    if event.registration_mode == Event.RegistrationMode.AUTOMATIC:
        _require_available_capacity(event)
        new_status = EventRegistration.Status.CONFIRMED
    else:
        new_status = EventRegistration.Status.PENDING

    if registration:
        # Reactivate a previously cancelled registration.
        registration.status = new_status
        registration.cancelled_at = None
    else:
        registration = EventRegistration(
            event=event,
            user=user,
            status=new_status,
        )

    return _save_registration(registration)


@transaction.atomic
def cancel_registration(*, event, user):
    """Cancel the authenticated user's own registration."""
    _require_authenticated(user)

    event = _get_locked_event(event)

    _require_public_event(event)

    registration = EventRegistration.objects.select_for_update().filter(
        event=event,
        user=user,
    ).first()

    if not registration:
        raise ValidationError(
            "You do not have a registration for this event."
        )

    if registration.status == EventRegistration.Status.CANCELLED:
        raise ValidationError(
            "Your registration is already cancelled."
        )

    if registration.status == EventRegistration.Status.REJECTED:
        raise ValidationError(
            "A rejected registration cannot be cancelled."
        )

    registration.status = EventRegistration.Status.CANCELLED
    registration.cancelled_at = timezone.now()

    return _save_registration(registration)


@transaction.atomic
def approve_registration(*, event, actor, registration_id):
    """Approve a pending registration."""
    _require_authenticated(actor)

    event = _get_locked_event(event)

    _require_public_event(event)
    _require_active_event(event)
    _require_registration_manager(actor, event)

    registration = _get_registration(event, registration_id)

    if registration.status != EventRegistration.Status.PENDING:
        raise ValidationError(
            "Only pending registrations can be approved."
        )

    _require_available_capacity(event)

    registration.status = EventRegistration.Status.CONFIRMED
    registration.cancelled_at = None

    return _save_registration(registration)


@transaction.atomic
def reject_registration(*, event, actor, registration_id):
    """Reject a pending registration."""
    _require_authenticated(actor)

    event = _get_locked_event(event)

    _require_public_event(event)
    _require_active_event(event)
    _require_registration_manager(actor, event)

    registration = _get_registration(event, registration_id)

    if registration.status != EventRegistration.Status.PENDING:
        raise ValidationError(
            "Only pending registrations can be rejected."
        )

    registration.status = EventRegistration.Status.REJECTED
    registration.cancelled_at = None

    return _save_registration(registration)
