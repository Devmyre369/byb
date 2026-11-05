
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from events.models import EventMedia
from events.services.permissions import can_moderate_media


def moderate_event_image(*, media, moderator, action):
    """
    Moderate an uploaded event image.

    Supported transitions:
        PENDING  -> APPROVED
        PENDING  -> REJECTED
        APPROVED -> REMOVED
    """

    transitions = {
        "approve": (
            EventMedia.ModerationStatus.PENDING,
            EventMedia.ModerationStatus.APPROVED,
        ),
        "reject": (
            EventMedia.ModerationStatus.PENDING,
            EventMedia.ModerationStatus.REJECTED,
        ),
        "remove": (
            EventMedia.ModerationStatus.APPROVED,
            EventMedia.ModerationStatus.REMOVED,
        ),
    }

    if action not in transitions:
        raise ValidationError({
            "action": "Invalid moderation action."
        })

    with transaction.atomic():
        locked_media = (
            EventMedia.objects
            .select_for_update()
            .select_related("event")
            .get(pk=media.pk)
        )

        if not can_moderate_media(moderator, locked_media.event):
            raise PermissionDenied(
                "You do not have permission to moderate this event's media."
            )

        expected_status, new_status = transitions[action]

        if locked_media.moderation_status != expected_status:
            raise ValidationError({
                "action": (
                    f"Cannot {action} an image with "
                    f"'{locked_media.moderation_status}' status."
                )
            })

        locked_media.moderation_status = new_status
        locked_media.save(update_fields=[
            "moderation_status",
            "updated_at",
        ])

        return locked_media
