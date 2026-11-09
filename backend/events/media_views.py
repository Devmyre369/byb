


import logging

from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Event, EventMedia
from events.media_serializers import EventMediaSerializer
from events.services.access import can_view_event
from events.services.media_service import (
    upload_event_cover_image,
    upload_event_image,
)


logger = logging.getLogger(__name__)


class EventCoverImageUploadView(APIView):
    """
    Upload an event cover image to Cloudinary.

    Cover images are stored separately from event gallery images.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image = request.FILES.get("image")

        if image is None:
            raise DRFValidationError({
                "image": "An image file is required."
            })

        try:
            cover_url = upload_event_cover_image(image=image)

        except ValidationError as exc:
            raise DRFValidationError(
                getattr(exc, "message_dict", None)
                or exc.messages
            )

        except Exception:
            logger.exception(
                "Unexpected error while uploading event cover image. "
                "User ID: %s",
                request.user.pk,
            )

            raise APIException(
                "The cover image could not be uploaded. Please try again."
            )

        return Response(
            {"cover_image": cover_url},
            status=status.HTTP_201_CREATED,
        )


class EventMediaUploadView(APIView):
    """
    Retrieve approved event gallery images and upload new images.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, event_id):
        event = get_object_or_404(
            Event,
            pk=event_id,
            is_deleted=False,
        )

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        media = (
            EventMedia.objects.filter(
                event=event,
                media_type=EventMedia.MediaType.IMAGE,
                moderation_status=EventMedia.ModerationStatus.APPROVED,
            )
            .select_related("uploaded_by")
        )

        serializer = EventMediaSerializer(
            media,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, event_id):
        event = get_object_or_404(
            Event,
            pk=event_id,
            is_deleted=False,
        )

        image = request.FILES.get("image")

        if image is None:
            raise DRFValidationError({
                "image": "An image file is required."
            })

        caption = request.data.get("caption", "")

        try:
            media = upload_event_image(
                event=event,
                uploaded_by=request.user,
                image=image,
                caption=caption,
            )

        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))

        except ValidationError as exc:
            raise DRFValidationError(
                getattr(exc, "message_dict", None)
                or exc.messages
            )

        except Exception:
            logger.exception(
                "Unexpected error while uploading event image. "
                "Event ID: %s",
                event_id,
            )

            raise APIException(
                "The image could not be uploaded. Please try again."
            )

        serializer = EventMediaSerializer(media)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
