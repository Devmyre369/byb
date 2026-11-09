
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from events.models import Event, EventMedia


User = get_user_model()


class MomentsFeedAPITests(APITestCase):

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
            title="BYB Moments Test Event",
            description="Testing the BYB Moments feed.",
            event_type=Event.EventType.SOCIAL,
            starts_at=timezone.now() + timedelta(days=2),
            visibility=Event.Visibility.PUBLIC,
            location_name="BBD University",
            city="Lucknow",
        )

        self.url = reverse("moments-feed")

        self.client = APIClient()
        self.client.force_authenticate(user=self.creator)

    def create_media(
        self,
        event=None,
        uploaded_by=None,
        moderation_status=EventMedia.ModerationStatus.APPROVED,
        public_id="test/moment",
        caption="A BYB moment",
    ):
        return EventMedia.objects.create(
            event=event or self.event,
            uploaded_by=uploaded_by or self.creator,
            media_type=EventMedia.MediaType.IMAGE,
            cloudinary_url=(
                "https://res.cloudinary.com/test/image/upload/"
                f"{public_id}.jpg"
            ),
            cloudinary_public_id=public_id,
            caption=caption,
            moderation_status=moderation_status,
        )

    # ------------------------------------------
    # HOME MOMENTS FEED TESTS
    # ------------------------------------------

    def test_unauthenticated_user_cannot_access_feed(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_approved_moment_appears_in_feed(self):
        media = self.create_media()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["count"], 1)

        moment = response.data["results"][0]

        self.assertEqual(str(moment["id"]), str(media.id))
        self.assertEqual(moment["caption"], "A BYB moment")
        self.assertEqual(moment["event"]["title"], self.event.title)
        self.assertEqual(moment["event"]["city"], "Lucknow")
        self.assertEqual(moment["uploader"]["username"], "creator")

    def test_unapproved_moments_do_not_appear_in_feed(self):
        self.create_media(
            moderation_status=EventMedia.ModerationStatus.PENDING,
            public_id="test/pending",
        )

        self.create_media(
            moderation_status=EventMedia.ModerationStatus.REJECTED,
            public_id="test/rejected",
        )

        self.create_media(
            moderation_status=EventMedia.ModerationStatus.REMOVED,
            public_id="test/removed",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_private_event_moments_are_hidden_from_unrelated_user(self):
        private_event = Event.objects.create(
            creator=self.other_user,
            title="Private Event",
            event_type=Event.EventType.PERSONAL,
            starts_at=timezone.now() + timedelta(days=2),
            visibility=Event.Visibility.PRIVATE,
        )

        self.create_media(
            event=private_event,
            uploaded_by=self.other_user,
            public_id="test/private",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["count"], 0)

    def test_deleted_event_moments_do_not_appear(self):
        deleted_event = Event.objects.create(
            creator=self.creator,
            title="Deleted Event",
            event_type=Event.EventType.SOCIAL,
            starts_at=timezone.now() + timedelta(days=2),
            visibility=Event.Visibility.PUBLIC,
            is_deleted=True,
            deleted_at=timezone.now(),
        )

        self.create_media(
            event=deleted_event,
            public_id="test/deleted",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["count"], 0)

    def test_feed_supports_pagination(self):
        for index in range(3):
            self.create_media(
                public_id=f"test/pagination_{index}",
                caption=f"Moment {index}",
            )

        response = self.client.get(
            self.url,
            {"page_size": 2},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])

    # ------------------------------------------
    # MY VIBES TESTS
    # ------------------------------------------

    def test_unauthenticated_user_cannot_access_my_moments(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("my-moments")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_see_own_moments_in_all_moderation_states(self):
        moderation_states = [
            EventMedia.ModerationStatus.PENDING,
            EventMedia.ModerationStatus.APPROVED,
            EventMedia.ModerationStatus.REJECTED,
            EventMedia.ModerationStatus.REMOVED,
        ]

        own_media = []

        for index, moderation_state in enumerate(moderation_states):
            media = self.create_media(
                moderation_status=moderation_state,
                public_id=f"test/my_moment_{index}",
            )
            own_media.append(media)

        other_event = Event.objects.create(
            creator=self.other_user,
            title="Other User Event",
            event_type=Event.EventType.PUBLIC,
            starts_at=timezone.now() + timedelta(days=3),
            visibility=Event.Visibility.PUBLIC,
            city="Lucknow",
        )

        other_media = self.create_media(
            event=other_event,
            uploaded_by=self.other_user,
            moderation_status=EventMedia.ModerationStatus.APPROVED,
            public_id="test/other_user_moment",
        )

        response = self.client.get(
            reverse("my-moments")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            len(own_media),
        )

        returned_ids = {
            str(moment["id"])
            for moment in response.data["results"]
        }

        expected_ids = {
            str(media.id)
            for media in own_media
        }

        self.assertSetEqual(returned_ids, expected_ids)

        returned_statuses = {
            moment["moderation_status"]
            for moment in response.data["results"]
        }

        self.assertSetEqual(
            returned_statuses,
            set(moderation_states),
        )

        self.assertNotIn(
            str(other_media.id),
            returned_ids,
        )

        for moment in response.data["results"]:
            self.assertEqual(
                moment["event"]["title"],
                self.event.title,
            )

    def test_my_moments_excludes_deleted_events(self):
        deleted_event = Event.objects.create(
            creator=self.creator,
            title="Deleted Vibe Event",
            event_type=Event.EventType.SOCIAL,
            starts_at=timezone.now() + timedelta(days=2),
            visibility=Event.Visibility.PUBLIC,
            is_deleted=True,
            deleted_at=timezone.now(),
        )

        self.create_media(
            event=deleted_event,
            public_id="test/deleted_my_moment",
        )

        response = self.client.get(
            reverse("my-moments")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_my_moments_supports_pagination(self):
        for index in range(3):
            self.create_media(
                public_id=f"test/my_pagination_{index}",
                caption=f"My moment {index}",
            )

        response = self.client.get(
            reverse("my-moments"),
            {"page_size": 2},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])
