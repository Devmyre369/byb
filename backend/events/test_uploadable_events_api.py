
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from events.models import (
    Event,
    EventOrganiser,
    EventParticipant,
    EventRegistration,
)


User = get_user_model()


class UploadableEventsAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            username="testuser",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="TestPassword123!",
        )

        self.url = reverse("uploadable-events")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def create_event(
        self,
        event_type,
        creator=None,
        title="Uploadable Test Event",
        event_status=Event.Status.UPCOMING,
        is_deleted=False,
    ):
        return Event.objects.create(
            creator=creator or self.other_user,
            title=title,
            event_type=event_type,
            starts_at=timezone.now() + timedelta(days=2),
            visibility=Event.Visibility.PUBLIC,
            status=event_status,
            is_deleted=is_deleted,
            deleted_at=timezone.now() if is_deleted else None,
            city="Lucknow",
        )

    def get_returned_event_ids(self, response):
        return {
            str(event["id"])
            for event in response.data["results"]
        }

    def test_unauthenticated_user_cannot_access_uploadable_events(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_event_creator_can_upload_to_all_event_types(self):
        event_types = [
            Event.EventType.PERSONAL,
            Event.EventType.SOCIAL,
            Event.EventType.PUBLIC,
        ]

        created_events = []

        for index, event_type in enumerate(event_types):
            created_events.append(
                self.create_event(
                    event_type=event_type,
                    creator=self.user,
                    title=f"Creator Event {index}",
                )
            )

        archived_event = self.create_event(
            event_type=Event.EventType.SOCIAL,
            creator=self.user,
            title="Archived Event",
            event_status=Event.Status.ARCHIVED,
        )

        deleted_event = self.create_event(
            event_type=Event.EventType.PUBLIC,
            creator=self.user,
            title="Deleted Event",
            is_deleted=True,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = self.get_returned_event_ids(response)

        expected_ids = {
            str(event.id)
            for event in created_events
        }

        self.assertSetEqual(returned_ids, expected_ids)

        self.assertNotIn(str(archived_event.id), returned_ids)
        self.assertNotIn(str(deleted_event.id), returned_ids)

    def test_personal_events_require_media_contributor_permission(self):
        invited_allowed = self.create_event(
            Event.EventType.PERSONAL,
            title="Invited Contributor Event",
        )

        accepted_allowed = self.create_event(
            Event.EventType.PERSONAL,
            title="Accepted Contributor Event",
        )

        invited_denied = self.create_event(
            Event.EventType.PERSONAL,
            title="Invited Without Permission",
        )

        accepted_denied = self.create_event(
            Event.EventType.PERSONAL,
            title="Accepted Without Permission",
        )

        EventParticipant.objects.create(
            event=invited_allowed,
            user=self.user,
            status=EventParticipant.Status.INVITED,
            can_upload_media=True,
        )

        EventParticipant.objects.create(
            event=accepted_allowed,
            user=self.user,
            status=EventParticipant.Status.ACCEPTED,
            can_upload_media=True,
        )

        EventParticipant.objects.create(
            event=invited_denied,
            user=self.user,
            status=EventParticipant.Status.INVITED,
            can_upload_media=False,
        )

        EventParticipant.objects.create(
            event=accepted_denied,
            user=self.user,
            status=EventParticipant.Status.ACCEPTED,
            can_upload_media=False,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = self.get_returned_event_ids(response)

        self.assertSetEqual(
            returned_ids,
            {
                str(invited_allowed.id),
                str(accepted_allowed.id),
            },
        )

    def test_social_events_require_accepted_participation(self):
        accepted_event = self.create_event(
            Event.EventType.SOCIAL,
            title="Accepted Social Event",
        )

        requested_event = self.create_event(
            Event.EventType.SOCIAL,
            title="Requested Social Event",
        )

        EventParticipant.objects.create(
            event=accepted_event,
            user=self.user,
            status=EventParticipant.Status.ACCEPTED,
            can_upload_media=False,
        )

        EventParticipant.objects.create(
            event=requested_event,
            user=self.user,
            status=EventParticipant.Status.REQUESTED,
            can_upload_media=True,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = self.get_returned_event_ids(response)

        self.assertSetEqual(
            returned_ids,
            {str(accepted_event.id)},
        )

    def test_public_events_require_confirmed_registration(self):
        confirmed_event = self.create_event(
            Event.EventType.PUBLIC,
            title="Confirmed Public Event",
        )

        pending_event = self.create_event(
            Event.EventType.PUBLIC,
            title="Pending Public Event",
        )

        cancelled_event = self.create_event(
            Event.EventType.PUBLIC,
            title="Cancelled Public Event",
        )

        EventRegistration.objects.create(
            event=confirmed_event,
            user=self.user,
            status=EventRegistration.Status.CONFIRMED,
        )

        EventRegistration.objects.create(
            event=pending_event,
            user=self.user,
            status=EventRegistration.Status.PENDING,
        )

        EventRegistration.objects.create(
            event=cancelled_event,
            user=self.user,
            status=EventRegistration.Status.CANCELLED,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = self.get_returned_event_ids(response)

        self.assertSetEqual(
            returned_ids,
            {str(confirmed_event.id)},
        )

    def test_co_organiser_needs_media_moderation_permission(self):
        allowed_event = self.create_event(
            Event.EventType.SOCIAL,
            title="Co-organiser With Permission",
        )

        denied_event = self.create_event(
            Event.EventType.SOCIAL,
            title="Co-organiser Without Permission",
        )

        EventOrganiser.objects.create(
            event=allowed_event,
            user=self.user,
            role=EventOrganiser.Role.CO_ORGANISER,
            can_moderate_media=True,
        )

        EventOrganiser.objects.create(
            event=denied_event,
            user=self.user,
            role=EventOrganiser.Role.CO_ORGANISER,
            can_moderate_media=False,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = self.get_returned_event_ids(response)

        self.assertSetEqual(
            returned_ids,
            {str(allowed_event.id)},
        )
