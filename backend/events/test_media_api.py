
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from events.models import Event, EventMedia


User = get_user_model()


class EventMediaAPITests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            email="creator@example.com",
            username="creator",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="TestPassword123!",
        )

        self.event = Event.objects.create(
            creator=self.creator,
            title="BYB Media Test Event",
            description="Testing BYB image uploads.",
            event_type=Event.EventType.SOCIAL,
            starts_at=timezone.now() + timedelta(days=2),
            visibility=Event.Visibility.PUBLIC,
        )

        self.url = reverse(
            "event-media-upload",
            kwargs={"event_id": self.event.id},
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.creator)

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

    def mock_cloudinary_upload(self, public_id):
        return {
            "secure_url": (
                "https://res.cloudinary.com/test/image/upload/"
                f"{public_id}.jpg"
            ),
            "public_id": public_id,
        }

    def create_media(
        self,
        moderation_status=EventMedia.ModerationStatus.APPROVED,
        public_id="test/image",
    ):
        return EventMedia.objects.create(
            event=self.event,
            uploaded_by=self.creator,
            media_type=EventMedia.MediaType.IMAGE,
            cloudinary_url=(
                f"https://res.cloudinary.com/test/image/upload/"
                f"{public_id}.jpg"
            ),
            cloudinary_public_id=public_id,
            caption="Test event image",
            moderation_status=moderation_status,
        )

    # --------------------------------------------------
    # IMAGE UPLOAD TESTS
    # --------------------------------------------------

    def test_unauthenticated_user_cannot_upload(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            {},
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(EventMedia.objects.count(), 0)

    def test_upload_requires_image_file(self):
        response = self.client.post(
            self.url,
            {"caption": "Missing image"},
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(EventMedia.objects.count(), 0)

    @patch(
        "events.services.media_service.cloudinary.uploader.upload"
    )
    def test_event_creator_can_upload_image(
        self,
        cloudinary_upload,
    ):
        cloudinary_upload.return_value = (
            self.mock_cloudinary_upload(
                "byb/events/test/api_image"
            )
        )

        image = self.make_image()

        response = self.client.post(
            self.url,
            {
                "image": image,
                "caption": "BYB event memory",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(EventMedia.objects.count(), 1)

        media = EventMedia.objects.get()

        self.assertEqual(media.event, self.event)
        self.assertEqual(media.uploaded_by, self.creator)
        self.assertEqual(
            media.media_type,
            EventMedia.MediaType.IMAGE,
        )
        self.assertEqual(media.caption, "BYB event memory")
        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.PENDING,
        )

        self.assertEqual(
            response.data["id"],
            str(media.id),
        )

        self.assertEqual(
            response.data["uploaded_by_id"],
            str(self.creator.id),
        )

        cloudinary_upload.assert_called_once()

    @patch(
        "events.services.media_service.cloudinary.uploader.upload"
    )
    def test_unrelated_user_cannot_upload_image(
        self,
        cloudinary_upload,
    ):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.post(
            self.url,
            {
                "image": self.make_image(),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(EventMedia.objects.count(), 0)
        cloudinary_upload.assert_not_called()

    @patch(
        "events.services.media_service.cloudinary.uploader.upload"
    )
    def test_invalid_image_format_is_rejected(
        self,
        cloudinary_upload,
    ):
        response = self.client.post(
            self.url,
            {
                "image": self.make_image("GIF"),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(EventMedia.objects.count(), 0)
        cloudinary_upload.assert_not_called()

    @patch(
        "events.services.media_service.cloudinary.uploader.upload",
        side_effect=RuntimeError("Cloudinary internal error"),
    )
    def test_cloudinary_failure_returns_safe_api_error(
        self,
        cloudinary_upload,
    ):
        response = self.client.post(
            self.url,
            {
                "image": self.make_image(),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        self.assertEqual(
            response.data["detail"],
            "The image could not be uploaded. Please try again.",
        )

        self.assertEqual(EventMedia.objects.count(), 0)
        cloudinary_upload.assert_called_once()

    def test_nonexistent_event_returns_404(self):
        nonexistent_url = reverse(
            "event-media-upload",
            kwargs={
                "event_id": "12345678-1234-5678-1234-567812345678"
            },
        )

        response = self.client.post(
            nonexistent_url,
            {
                "image": self.make_image(),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertEqual(EventMedia.objects.count(), 0)

    # --------------------------------------------------
    # EVENT GALLERY RETRIEVAL TESTS
    # --------------------------------------------------

    def test_event_creator_can_retrieve_approved_gallery_images(self):
        approved_image = self.create_media(
            moderation_status=EventMedia.ModerationStatus.APPROVED,
            public_id="gallery/approved",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["id"],
            str(approved_image.id),
        )

        self.assertEqual(
            response.data[0]["moderation_status"],
            EventMedia.ModerationStatus.APPROVED,
        )

    def test_gallery_excludes_unapproved_images(self):
        self.create_media(
            EventMedia.ModerationStatus.APPROVED,
            "gallery/approved",
        )

        self.create_media(
            EventMedia.ModerationStatus.PENDING,
            "gallery/pending",
        )

        self.create_media(
            EventMedia.ModerationStatus.REJECTED,
            "gallery/rejected",
        )

        self.create_media(
            EventMedia.ModerationStatus.REMOVED,
            "gallery/removed",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["moderation_status"],
            EventMedia.ModerationStatus.APPROVED,
        )

    def test_unauthenticated_user_cannot_retrieve_gallery(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unrelated_user_cannot_view_private_event_gallery(self):
        self.event.visibility = Event.Visibility.PRIVATE
        self.event.save(update_fields=["visibility"])

        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_creator_can_retrieve_archived_event_gallery(self):
        self.event.status = Event.Status.ARCHIVED
        self.event.save(update_fields=["status"])

        self.create_media(
            EventMedia.ModerationStatus.APPROVED,
            "gallery/archived",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

    @patch(
        "events.services.media_service.cloudinary.uploader.upload"
    )
    def test_gallery_viewer_does_not_gain_upload_permission(
        self,
        cloudinary_upload,
    ):
        self.client.force_authenticate(
            user=self.other_user
        )

        # Public event: the user can view its gallery.
        gallery_response = self.client.get(self.url)

        self.assertEqual(
            gallery_response.status_code,
            status.HTTP_200_OK,
        )

        # Gallery access does not grant image-upload permission.
        upload_response = self.client.post(
            self.url,
            {
                "image": self.make_image(),
            },
            format="multipart",
        )

        self.assertEqual(
            upload_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(EventMedia.objects.count(), 0)
        cloudinary_upload.assert_not_called()