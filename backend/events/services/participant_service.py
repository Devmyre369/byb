from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from events.models import Event, EventOrganiser, EventParticipant
from events.services.permissions import can_manage_participants


def _require_authenticated(user):
    if not user or not user.is_authenticated:
        raise PermissionDenied("You must be logged in to perform this action.")


def _get_locked_event(event):
    """Fetch and lock the event so concurrent participation changes are serialized."""
    if not event or not event.pk:
        raise ValidationError("A valid event is required.")

    locked_event = Event.objects.select_for_update().get(pk=event.pk)

    if locked_event.is_deleted:
        raise ValidationError("This event is no longer available.")

    if locked_event.status in (
        Event.Status.COMPLETED,
        Event.Status.ARCHIVED,
    ):
        raise ValidationError("Participation is closed for this event.")

    return locked_event


def _require_social_event(event):
    if event.event_type != Event.EventType.SOCIAL:
        raise ValidationError(
            "Participant management is currently available only for Social events."
        )


def _require_participant_manager(actor, event):
    _require_authenticated(actor)

    if not can_manage_participants(actor, event):
        raise PermissionDenied(
            "You do not have permission to manage this event's participants."
        )


def _require_available_capacity(event):
    if event.capacity is None:
        return

    accepted_count = EventParticipant.objects.filter(
        event=event,
        status=EventParticipant.Status.ACCEPTED,
    ).count()

    if accepted_count >= event.capacity:
        raise ValidationError("This event has reached its participant capacity.")


def _get_participant(event, user):
    participant = (
        EventParticipant.objects.select_for_update()
        .filter(event=event, user=user)
        .first()
    )

    if participant is None:
        raise ValidationError("This participation record does not exist.")

    return participant


def _save_participant(participant):
    participant.full_clean()
    participant.save()
    return participant


def _ensure_not_organiser(event, user):
    if event.creator_id == user.pk:
        raise ValidationError("The event creator cannot join as a participant.")

    if EventOrganiser.objects.filter(event=event, user=user).exists():
        raise ValidationError("An event organiser cannot join as a participant.")


@transaction.atomic
def request_to_join_event(*, event, user):
    """Allow an authenticated user to request participation in a public Social event."""
    _require_authenticated(user)

    event = _get_locked_event(event)
    _require_social_event(event)

    if event.visibility != Event.Visibility.PUBLIC:
        raise ValidationError(
            "This event is not open to public join requests. Ask an organiser for an invitation."
        )

    _ensure_not_organiser(event, user)

    participant = (
        EventParticipant.objects.select_for_update()
        .filter(event=event, user=user)
        .first()
    )

    if participant:
        if participant.status == EventParticipant.Status.ACCEPTED:
            raise ValidationError("You are already participating in this event.")

        if participant.status == EventParticipant.Status.INVITED:
            raise ValidationError(
                "You already have an invitation. Respond to that invitation instead."
            )

        if participant.status == EventParticipant.Status.REQUESTED:
            raise ValidationError("Your join request is already pending.")

        if participant.status not in (
            EventParticipant.Status.DECLINED,
            EventParticipant.Status.LEFT,
            EventParticipant.Status.REMOVED,
        ):
            raise ValidationError("You cannot request to join this event.")

        participant.status = EventParticipant.Status.REQUESTED
        participant.can_upload_media = False
        participant.invited_by = None
        return _save_participant(participant)

    participant = EventParticipant(
        event=event,
        user=user,
        status=EventParticipant.Status.REQUESTED,
        can_upload_media=False,
    )

    return _save_participant(participant)


@transaction.atomic
def invite_to_event(*, event, actor, user):
    """Invite a user to a Social event."""
    _require_authenticated(actor)
    _require_authenticated(user)

    event = _get_locked_event(event)
    _require_social_event(event)
    _require_participant_manager(actor, event)
    _ensure_not_organiser(event, user)

    participant = (
        EventParticipant.objects.select_for_update()
        .filter(event=event, user=user)
        .first()
    )

    if participant:
        if participant.status in (
            EventParticipant.Status.INVITED,
            EventParticipant.Status.REQUESTED,
            EventParticipant.Status.ACCEPTED,
        ):
            raise ValidationError(
                "This user already has an active invitation or participation record."
            )

        if participant.status not in (
            EventParticipant.Status.DECLINED,
            EventParticipant.Status.LEFT,
            EventParticipant.Status.REMOVED,
        ):
            raise ValidationError("This user cannot be invited.")

        participant.status = EventParticipant.Status.INVITED
        participant.invited_by = actor
        participant.can_upload_media = False
        return _save_participant(participant)

    participant = EventParticipant(
        event=event,
        user=user,
        status=EventParticipant.Status.INVITED,
        invited_by=actor,
        can_upload_media=False,
    )

    return _save_participant(participant)


@transaction.atomic
def respond_to_invitation(*, event, user, accept):
    """Accept or decline the authenticated user's own invitation."""
    _require_authenticated(user)

    if not isinstance(accept, bool):
        raise ValidationError("The invitation response must be true or false.")

    event = _get_locked_event(event)
    _require_social_event(event)

    participant = _get_participant(event, user)

    if participant.status != EventParticipant.Status.INVITED:
        raise ValidationError("There is no pending invitation to respond to.")

    if accept:
        _require_available_capacity(event)
        participant.status = EventParticipant.Status.ACCEPTED
        participant.joined_at = timezone.now()
        participant.can_upload_media = True
    else:
        participant.status = EventParticipant.Status.DECLINED
        participant.can_upload_media = False

    return _save_participant(participant)


@transaction.atomic
def approve_join_request(*, event, actor, participant_id):
    """Approve a pending Social event join request."""
    _require_authenticated(actor)

    event = _get_locked_event(event)
    _require_social_event(event)
    _require_participant_manager(actor, event)

    participant = (
        EventParticipant.objects.select_for_update()
        .filter(event=event, pk=participant_id)
        .first()
    )

    if participant is None:
        raise ValidationError("The participant record does not exist.")

    if participant.status != EventParticipant.Status.REQUESTED:
        raise ValidationError("This join request is no longer pending.")

    _require_available_capacity(event)

    participant.status = EventParticipant.Status.ACCEPTED
    participant.joined_at = timezone.now()
    participant.can_upload_media = True

    return _save_participant(participant)


@transaction.atomic
def decline_join_request(*, event, actor, participant_id):
    """Decline a pending Social event join request."""
    _require_authenticated(actor)

    event = _get_locked_event(event)
    _require_social_event(event)
    _require_participant_manager(actor, event)

    participant = (
        EventParticipant.objects.select_for_update()
        .filter(event=event, pk=participant_id)
        .first()
    )

    if participant is None:
        raise ValidationError("The participant record does not exist.")

    if participant.status != EventParticipant.Status.REQUESTED:
        raise ValidationError("This join request is no longer pending.")

    participant.status = EventParticipant.Status.DECLINED
    participant.can_upload_media = False

    return _save_participant(participant)


@transaction.atomic
def leave_event(*, event, user):
    """Allow a participant to leave their own Social event."""
    _require_authenticated(user)

    event = _get_locked_event(event)
    _require_social_event(event)

    participant = _get_participant(event, user)

    if participant.status not in (
        EventParticipant.Status.INVITED,
        EventParticipant.Status.REQUESTED,
        EventParticipant.Status.ACCEPTED,
    ):
        raise ValidationError("You do not have an active participation record.")

    participant.status = EventParticipant.Status.LEFT
    participant.can_upload_media = False

    return _save_participant(participant)


@transaction.atomic
def remove_participant(*, event, actor, participant_id):
    """Allow an authorised organiser to remove a participant."""
    _require_authenticated(actor)

    event = _get_locked_event(event)
    _require_social_event(event)
    _require_participant_manager(actor, event)

    participant = (
        EventParticipant.objects.select_for_update()
        .filter(event=event, pk=participant_id)
        .first()
    )

    if participant is None:
        raise ValidationError("The participant record does not exist.")

    if participant.status not in (
        EventParticipant.Status.INVITED,
        EventParticipant.Status.REQUESTED,
        EventParticipant.Status.ACCEPTED,
    ):
        raise ValidationError("This participant does not have an active participation record.")

    participant.status = EventParticipant.Status.REMOVED
    participant.can_upload_media = False

    return _save_participant(participant)