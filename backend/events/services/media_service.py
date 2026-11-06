
import logging
import uuid

import cloudinary.uploader
from PIL import Image, UnidentifiedImageError

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from events.models import EventMedia
from events.services.permissions import can_upload_event_media


logger = logging.getLogger(__name__)


MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}

MAX_IMAGE_PIXELS = 40_000_000


def validate_event_image(image):
    """
    Validate an uploaded image using its actual contents.

    Allowed formats: JPEG, PNG, WebP.
    Maximum size: 10 MB.
    Maximum dimensions: 40 million pixels.
    """

    if not image:
        raise ValidationError("An image file is required.")

    if not hasattr(image, "read") or not hasattr(image, "seek"):
        raise ValidationError("Invalid image upload.")

    file_size = getattr(image, "size", None)

    if file_size is None:
        raise ValidationError("Unable to determine image size.")

    if file_size <= 0:
        raise ValidationError("The uploaded image is empty.")

    if file_size > MAX_IMAGE_SIZE:
        raise ValidationError("Image size cannot exceed 10 MB.")

    try:
        image.seek(0)

        with Image.open(image) as img:
            image_format = img.format

            if image_format not in ALLOWED_IMAGE_FORMATS:
                raise ValidationError(
                    "Only JPEG, PNG and WebP images are supported."
                )

            width, height = img.size

            if width <= 0 or height <= 0:
                raise ValidationError("Invalid image dimensions.")

            if width * height > MAX_IMAGE_PIXELS:
                raise ValidationError(
                    "Image dimensions are too large."
                )

            if getattr(img, "n_frames", 1) != 1:
                raise ValidationError(
                    "Animated images are not supported."
                )

            img.verify()

        image.seek(0)

        # Reopen and fully decode the image to catch corrupt image data.
        with Image.open(image) as img:
            img.load()

    except ValidationError:
        raise

    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise ValidationError(
            "The uploaded file is not a valid supported image."
        ) from exc

    finally:
        image.seek(0)

    return image_format


def upload_event_image(
    *,
    event,
    uploaded_by,
    image,
    caption="",
):
    """
    Upload an event gallery image to Cloudinary.

    Creates an EventMedia record.
    New uploads remain pending moderation until approved.
    """

    if not can_upload_event_media(uploaded_by, event):
        raise PermissionDenied(
            "You do not have permission to upload media to this event."
        )

    if not isinstance(caption, str):
        raise ValidationError("Caption must be text.")

    caption = caption.strip()

    if len(caption) > 500:
        raise ValidationError(
            "Caption cannot exceed 500 characters."
        )

    validate_event_image(image)

    public_id = f"event_{uuid.uuid4().hex}"

    cloudinary_folder = f"byb/events/{event.id}"

    upload_result = None

    try:
        upload_result = cloudinary.uploader.upload(
            image,
            resource_type="image",
            folder=cloudinary_folder,
            public_id=public_id,
            overwrite=False,
            unique_filename=False,
            use_filename=False,
            allowed_formats=["jpg", "jpeg", "png", "webp"],
        )

        secure_url = upload_result.get("secure_url")
        cloudinary_public_id = upload_result.get("public_id")

        if not secure_url or not cloudinary_public_id:
            raise RuntimeError(
                "Cloudinary returned an incomplete upload response."
            )

        with transaction.atomic():
            media = EventMedia.objects.create(
                event=event,
                uploaded_by=uploaded_by,
                media_type=EventMedia.MediaType.IMAGE,
                cloudinary_url=secure_url,
                cloudinary_public_id=cloudinary_public_id,
                caption=caption,
                moderation_status=(
                    EventMedia.ModerationStatus.PENDING
                ),
            )

        return media

    except Exception:
        # If Cloudinary succeeded but database creation failed,
        # remove the uploaded image to avoid orphaned files.
        if upload_result:
            uploaded_public_id = upload_result.get("public_id")

            if uploaded_public_id:
                try:
                    cloudinary.uploader.destroy(
                        uploaded_public_id,
                        resource_type="image",
                    )
                except Exception:
                    logger.exception(
                        "Failed to clean up Cloudinary image %s",
                        uploaded_public_id,
                    )

        raise


def upload_event_cover_image(*, image):
    """
    Upload an event cover image to Cloudinary.

    Cover images are stored separately from event gallery images.
    Returns the secure URL without creating an EventMedia record.
    """

    validate_event_image(image)

    public_id = f"cover_{uuid.uuid4().hex}"

    upload_result = None

    try:
        upload_result = cloudinary.uploader.upload(
            image,
            resource_type="image",
            folder="byb/event-covers",
            public_id=public_id,
            overwrite=False,
            unique_filename=False,
            use_filename=False,
            allowed_formats=["jpg", "jpeg", "png", "webp"],
        )

        secure_url = upload_result.get("secure_url")

        if not secure_url:
            raise RuntimeError(
                "Cloudinary returned an incomplete upload response."
            )

        return secure_url

    except Exception:
        # Clean up the uploaded file if the operation fails.
        if upload_result:
            uploaded_public_id = upload_result.get("public_id")

            if uploaded_public_id:
                try:
                    cloudinary.uploader.destroy(
                        uploaded_public_id,
                        resource_type="image",
                    )
                except Exception:
                    logger.exception(
                        "Failed to clean up Cloudinary cover image %s",
                        uploaded_public_id,
                    )

        raise
