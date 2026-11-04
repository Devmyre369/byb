from django.test import TestCase

# Create your tests here.
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from events.models import Event, EventOrganiser


User = get_user_model()


class EventAPITests(APITestCase):

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

        self.client = APIClient()
        self.client.force_authenticate(user=self.creator)

        self.list_url = reverse("event-list-create")

        self.event_data = {
            "title": "BYB Launch Meetup",
            "description": "A test event for BYB.",
            "event_type": Event.EventType.SOCIAL,
            "category": "Technology",
            "starts_at": (
                timezone.now() + timedelta(days=7)
            ).isoformat(),
            "visibility": Event.Visibility.PUBLIC,
            "city": "Lucknow",
        }

    def create_event(self, **overrides):
        data = {
            **self.event_data,
            **overrides,
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        return Event.objects.get(pk=response.data["id"])

    def test_authenticated_user_can_create_event(self):
        event = self.create_event()

        self.assertEqual(event.creator, self.creator)
        self.assertEqual(event.title, "BYB Launch Meetup")
        self.assertEqual(
            event.event_type,
            Event.EventType.SOCIAL,
        )

    def test_event_creator_is_automatically_primary_organiser(self):
        event = self.create_event()

        organiser = EventOrganiser.objects.get(
            event=event,
            user=self.creator,
        )

        self.assertEqual(
            organiser.role,
            EventOrganiser.Role.PRIMARY,
        )

    def test_creator_can_retrieve_own_event(self):
        event = self.create_event()

        detail_url = reverse(
            "event-detail",
            kwargs={"event_id": event.id},
        )

        response = self.client.get(detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["id"], str(event.id))

    def test_creator_can_edit_own_event(self):
        event = self.create_event()

        detail_url = reverse(
            "event-detail",
            kwargs={"event_id": event.id},
        )

        response = self.client.patch(
            detail_url,
            {"title": "Updated BYB Meetup"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        event.refresh_from_db()

        self.assertEqual(
            event.title,
            "Updated BYB Meetup",
        )

    def test_other_user_cannot_view_private_event(self):
        event = self.create_event(
            visibility=Event.Visibility.PRIVATE,
        )

        self.client.force_authenticate(user=self.other_user)

        detail_url = reverse(
            "event-detail",
            kwargs={"event_id": event.id},
        )

        response = self.client.get(detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_deleted_event_cannot_be_retrieved(self):
        event = self.create_event()

        detail_url = reverse(
            "event-detail",
            kwargs={"event_id": event.id},
        )

        delete_response = self.client.delete(detail_url)

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        event.refresh_from_db()

        self.assertTrue(event.is_deleted)
        self.assertIsNotNone(event.deleted_at)

        get_response = self.client.get(detail_url)

        self.assertEqual(
            get_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_public_event_cannot_be_created_in_the_past(self):
        past_date = (
            timezone.now() - timedelta(days=2)
        ).isoformat()

        response = self.client.post(
            self.list_url,
            {
                **self.event_data,
                "event_type": Event.EventType.PUBLIC,
                "starts_at": past_date,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("starts_at", response.data)