
from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from events.models import (
    Event,
    EventMedia,
    EventOrganiser,
)


User = get_user_model()


class EventMediaModerationAPITests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            email="moderator_creator@example.com",
            username="moderator_creator",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="moderator_other@example.com",
            username="moderator_other",
            password="TestPassword123!",
        )

        self.co_organiser = User.objects.create_user(
            email="moderator_co@example.com",
            username="moderator_co",
            password="TestPassword123!",
        )

        self.event = Event.objects.create(
            creator=self.creator,
            title="BYB Moderation Test Event",
            description="Testing event image moderation.",
            event_type=Event.EventType.SOCIAL,
            starts_at=timezone.now() + timedelta(days=2),
            visibility=Event.Visibility.PUBLIC,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.creator)

    def create_media(
        self,
        moderation_status=EventMedia.ModerationStatus.PENDING,
        event=None,
    ):
        return EventMedia.objects.create(
            event=event or self.event,
            uploaded_by=self.creator,
            media_type=EventMedia.MediaType.IMAGE,
            cloudinary_url=(
                "https://res.cloudinary.com/test/image/upload/"
                f"{uuid4()}.jpg"
            ),
            cloudinary_public_id=f"byb/events/test/{uuid4()}",
            caption="Moderation test image",
            moderation_status=moderation_status,
        )

    def get_moderation_url(self, media):
        return reverse(
            "event-media-moderate",
            kwargs={
                "event_id": media.event_id,
                "media_id": media.id,
            },
        )

    def moderate(self, media, action):
        return self.client.post(
            self.get_moderation_url(media),
            {"action": action},
            format="json",
        )

    def test_creator_can_approve_pending_image(self):
        media = self.create_media()

        response = self.moderate(media, "approve")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.APPROVED,
        )

        self.assertEqual(
            response.data["moderation_status"],
            EventMedia.ModerationStatus.APPROVED,
        )

    def test_creator_can_reject_pending_image(self):
        media = self.create_media()

        response = self.moderate(media, "reject")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.REJECTED,
        )

    def test_creator_can_remove_approved_image(self):
        media = self.create_media(
            moderation_status=EventMedia.ModerationStatus.APPROVED,
        )

        response = self.moderate(media, "remove")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.REMOVED,
        )

    def test_co_organiser_with_permission_can_moderate(self):
        EventOrganiser.objects.create(
            event=self.event,
            user=self.co_organiser,
            role=EventOrganiser.Role.CO_ORGANISER,
            can_moderate_media=True,
        )

        self.client.force_authenticate(
            user=self.co_organiser,
        )

        media = self.create_media()

        response = self.moderate(media, "approve")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.APPROVED,
        )

    def test_co_organiser_without_permission_cannot_moderate(self):
        EventOrganiser.objects.create(
            event=self.event,
            user=self.co_organiser,
            role=EventOrganiser.Role.CO_ORGANISER,
            can_moderate_media=False,
        )

        self.client.force_authenticate(
            user=self.co_organiser,
        )

        media = self.create_media()

        response = self.moderate(media, "approve")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.PENDING,
        )

    def test_unrelated_user_cannot_moderate(self):
        self.client.force_authenticate(
            user=self.other_user,
        )

        media = self.create_media()

        response = self.moderate(media, "approve")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.PENDING,
        )

    def test_unauthenticated_user_cannot_moderate(self):
        media = self.create_media()

        self.client.force_authenticate(user=None)

        response = self.moderate(media, "approve")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.PENDING,
        )

    def test_cannot_approve_already_approved_image(self):
        media = self.create_media(
            moderation_status=EventMedia.ModerationStatus.APPROVED,
        )

        response = self.moderate(media, "approve")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.APPROVED,
        )

    def test_cannot_reject_already_approved_image(self):
        media = self.create_media(
            moderation_status=EventMedia.ModerationStatus.APPROVED,
        )

        response = self.moderate(media, "reject")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.APPROVED,
        )

    def test_invalid_moderation_action_is_rejected(self):
        media = self.create_media()

        response = self.moderate(media, "publish")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.PENDING,
        )

    def test_media_from_another_event_returns_404(self):
        another_event = Event.objects.create(
            creator=self.creator,
            title="Another BYB Event",
            description="A separate event.",
            event_type=Event.EventType.SOCIAL,
            starts_at=timezone.now() + timedelta(days=3),
            visibility=Event.Visibility.PUBLIC,
        )

        media = self.create_media(event=another_event)

        # Deliberately use the original event ID with
        # the media ID belonging to another event.
        url = reverse(
            "event-media-moderate",
            kwargs={
                "event_id": self.event.id,
                "media_id": media.id,
            },
        )

        response = self.client.post(
            url,
            {"action": "approve"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        media.refresh_from_db()

        self.assertEqual(
            media.moderation_status,
            EventMedia.ModerationStatus.PENDING,
        )
