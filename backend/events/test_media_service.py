
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from events.models import Event, EventMedia, EventParticipant
from events.services.media_service import (
    MAX_IMAGE_SIZE,
    upload_event_image,
    validate_event_image,
)


User = get_user_model()


class EventMediaServiceTests(TestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            email="creator@example.com",
            username="creator",
            password="TestPassword123!",
        )

        self.attendee = User.objects.create_user(
            email="attendee@example.com",
            username="attendee",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="TestPassword123!",
        )

        self.event = Event.objects.create(
            creator=self.creator,
            title="BYB Test Event",
            description="Testing event media uploads.",
            event_type=Event.EventType.SOCIAL,
            starts_at=timezone.now() + timedelta(days=2),
            visibility=Event.Visibility.PUBLIC,
        )

    def make_image(self, image_format="JPEG"):
        buffer = BytesIO()

        Image.new(
            "RGB",
            (100, 100),
            color="red",
        ).save(buffer, format=image_format)

        extension = {
            "JPEG": "jpg",
            "PNG": "png",
            "WEBP": "webp",
            "GIF": "gif",
        }[image_format]

        content_type = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "WEBP": "image/webp",
            "GIF": "image/gif",
        }[image_format]

        return SimpleUploadedFile(
            f"test_image.{extension}",
            buffer.getvalue(),
            content_type=content_type,
        )

    # Image validation tests

    def test_jpeg_image_is_valid(self):
        image = self.make_image("JPEG")

        self.assertEqual(
            validate_event_image(image),
            "JPEG",
        )

    def test_png_image_is_valid(self):
        image = self.make_image("PNG")

        self.assertEqual(
            validate_event_image(image),
            "PNG",
        )

    def test_webp_image_is_valid(self):
        image = self.make_image("WEBP")

        self.assertEqual(
            validate_event_image(image),
            "WEBP",
        )

    def test_gif_image_is_rejected(self):
        image = self.make_image("GIF")

        with self.assertRaises(ValidationError):
            validate_event_image(image)

    def test_invalid_file_is_rejected(self):
        image = SimpleUploadedFile(
            "fake.jpg",
            b"This is not an image.",
            content_type="image/jpeg",
        )

        with self.assertRaises(ValidationError):
            validate_event_image(image)

    def test_empty_file_is_rejected(self):
        image = SimpleUploadedFile(
            "empty.jpg",
            b"",
            content_type="image/jpeg",
        )

        with self.assertRaises(ValidationError):
            validate_event_image(image)

    def test_image_over_10_mb_is_rejected(self):
        image = SimpleUploadedFile(
            "large.jpg",
            b"x" * (MAX_IMAGE_SIZE + 1),
            content_type="image/jpeg",
        )

        with self.assertRaises(ValidationError):
            validate_event_image(image)

    # Upload permission and service tests

    def test_event_creator_can_upload_image(self):
        image = self.make_image()

        with patch(
            "events.services.media_service.cloudinary.uploader.upload"
        ) as cloudinary_upload:

            cloudinary_upload.return_value = {
                "secure_url": "https://res.cloudinary.com/test/image.jpg",
                "public_id": "byb/events/test/event_image",
            }

            media = upload_event_image(
                event=self.event,
                uploaded_by=self.creator,
                image=image,
                caption="BYB event memory",
            )

        self.assertEqual(media.event, self.event)
        self.assertEqual(media.uploaded_by, self.creator)
        self.assertEqual(media.media_type, EventMedia.MediaType.IMAGE)

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.PENDING,
        )

        self.assertEqual(media.caption, "BYB event memory")
        cloudinary_upload.assert_called_once()

    def test_accepted_social_participant_can_upload(self):
        EventParticipant.objects.create(
            event=self.event,
            user=self.attendee,
            status=EventParticipant.Status.ACCEPTED,
        )

        image = self.make_image()

        with patch(
            "events.services.media_service.cloudinary.uploader.upload"
        ) as cloudinary_upload:

            cloudinary_upload.return_value = {
                "secure_url": "https://res.cloudinary.com/test/image.jpg",
                "public_id": "byb/events/test/participant_image",
            }

            media = upload_event_image(
                event=self.event,
                uploaded_by=self.attendee,
                image=image,
            )

        self.assertEqual(media.uploaded_by, self.attendee)

    def test_unrelated_user_cannot_upload(self):
        image = self.make_image()

        with self.assertRaises(PermissionDenied):
            upload_event_image(
                event=self.event,
                uploaded_by=self.other_user,
                image=image,
            )

    def test_cloudinary_failure_does_not_create_media_record(self):
        image = self.make_image()

        with patch(
            "events.services.media_service.cloudinary.uploader.upload",
            side_effect=RuntimeError("Cloudinary upload failed"),
        ):
            with self.assertRaises(RuntimeError):
                upload_event_image(
                    event=self.event,
                    uploaded_by=self.creator,
                    image=image,
                )

        self.assertEqual(EventMedia.objects.count(), 0)

    def test_database_failure_triggers_cloudinary_cleanup(self):
        image = self.make_image()

        with patch(
            "events.services.media_service.cloudinary.uploader.upload"
        ) as cloudinary_upload, patch(
            "events.services.media_service.cloudinary.uploader.destroy"
        ) as cloudinary_destroy, patch(
            "events.services.media_service.EventMedia.objects.create",
            side_effect=RuntimeError("Database save failed"),
        ):

            cloudinary_upload.return_value = {
                "secure_url": "https://res.cloudinary.com/test/image.jpg",
                "public_id": "byb/events/test/cleanup_image",
            }

            with self.assertRaises(RuntimeError):
                upload_event_image(
                    event=self.event,
                    uploaded_by=self.creator,
                    image=image,
                )

        cloudinary_destroy.assert_called_once_with(
            "byb/events/test/cleanup_image",
            resource_type="image",
        )

        self.assertEqual(EventMedia.objects.count(), 0)

    def test_caption_over_500_characters_is_rejected(self):
        image = self.make_image()

        with self.assertRaises(ValidationError):
            upload_event_image(
                event=self.event,
                uploaded_by=self.creator,
                image=image,
                caption="A" * 501,
            )

    def test_archived_event_rejects_upload(self):
        self.event.status = Event.Status.ARCHIVED
        self.event.archived_at = timezone.now()
        self.event.save()

        image = self.make_image()

        with self.assertRaises(PermissionDenied):
            upload_event_image(
                event=self.event,
                uploaded_by=self.creator,
                image=image,
            )
