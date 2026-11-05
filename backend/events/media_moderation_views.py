
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import (
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Event, EventMedia
from events.media_serializers import EventMediaSerializer
from events.services.media_moderation_service import (
    moderate_event_image,
)


class EventMediaModerationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id, media_id):
        event = get_object_or_404(
            Event,
            pk=event_id,
            is_deleted=False,
        )

        media = get_object_or_404(
            EventMedia,
            pk=media_id,
            event=event,
            media_type=EventMedia.MediaType.IMAGE,
        )

        action = request.data.get("action")

        if not isinstance(action, str):
            raise DRFValidationError({
                "action": "A moderation action is required."
            })

        try:
            moderated_media = moderate_event_image(
                media=media,
                moderator=request.user,
                action=action.strip().lower(),
            )

        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))

        except ValidationError as exc:
            raise DRFValidationError(
                getattr(exc, "message_dict", None)
                or exc.messages
            )

        serializer = EventMediaSerializer(moderated_media)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
