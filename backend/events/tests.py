

from datetime import timedelta
from events.services.permissions import can_upload_event_media
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
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

from events.services.organiser_service import (
    add_co_organiser,
    update_co_organiser_permissions,
    remove_co_organiser,
)

from events.services.participant_service import (
    request_to_join_event,
    invite_to_event,
    respond_to_invitation,
    approve_join_request,
    decline_join_request,
    leave_event,
    remove_participant,
)


User = get_user_model()


# ======================================================
# EVENT API TESTS
# ======================================================

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

        self.third_user = User.objects.create_user(
            email="third@example.com",
            username="thirduser",
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

    def get_detail_url(self, event):
        return reverse(
            "event-detail",
            kwargs={"event_id": event.id},
        )

    # --------------------------------------------------
    # Original event tests
    # --------------------------------------------------

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

        response = self.client.get(self.get_detail_url(event))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data["id"], str(event.id))

    def test_creator_can_edit_own_event(self):
        event = self.create_event()

        response = self.client.patch(
            self.get_detail_url(event),
            {"title": "Updated BYB Meetup"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        event.refresh_from_db()
        self.assertEqual(event.title, "Updated BYB Meetup")

    def test_other_user_cannot_view_private_event(self):
        event = self.create_event(
            visibility=Event.Visibility.PRIVATE,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.get_detail_url(event))

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_deleted_event_cannot_be_retrieved(self):
        event = self.create_event()
        detail_url = self.get_detail_url(event)

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

    # --------------------------------------------------
    # Access-control tests
    # --------------------------------------------------

    def test_authenticated_user_can_view_public_event(self):
        event = self.create_event()

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.get_detail_url(event))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_private_event_is_excluded_from_other_users_feed(self):
        event = self.create_event(
            visibility=Event.Visibility.PRIVATE,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        event_ids = [
            item["id"] for item in response.data["results"]
        ]

        self.assertNotIn(str(event.id), event_ids)

    def test_accepted_social_participant_can_view_selected_event(self):
        event = self.create_event(
            visibility=Event.Visibility.SELECTED,
        )

        EventParticipant.objects.create(
            event=event,
            user=self.other_user,
            status=EventParticipant.Status.ACCEPTED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.get_detail_url(event))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_confirmed_public_registration_grants_selected_event_access(self):
        event = self.create_event(
            event_type=Event.EventType.PUBLIC,
            visibility=Event.Visibility.SELECTED,
        )

        EventRegistration.objects.create(
            event=event,
            user=self.other_user,
            status=EventRegistration.Status.CONFIRMED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.get_detail_url(event))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_archived_event_is_hidden_from_feed(self):
        event = self.create_event()

        Event.objects.filter(pk=event.pk).update(
            status=Event.Status.ARCHIVED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        event_ids = [
            item["id"] for item in response.data["results"]
        ]

        self.assertNotIn(str(event.id), event_ids)

    def test_archived_event_remains_accessible_to_accepted_participant(self):
        event = self.create_event(
            visibility=Event.Visibility.PUBLIC,
        )

        EventParticipant.objects.create(
            event=event,
            user=self.other_user,
            status=EventParticipant.Status.ACCEPTED,
        )

        Event.objects.filter(pk=event.pk).update(
            status=Event.Status.ARCHIVED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.get_detail_url(event))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # Co-organiser service tests
    # --------------------------------------------------

    def test_primary_organiser_can_add_co_organiser(self):
        event = self.create_event()

        organiser = add_co_organiser(
            event=event,
            actor=self.creator,
            user=self.other_user,
            permissions={
                "can_edit_event": True,
                "can_moderate_media": True,
            },
        )

        self.assertEqual(organiser.event, event)
        self.assertEqual(organiser.user, self.other_user)
        self.assertEqual(
            organiser.role,
            EventOrganiser.Role.CO_ORGANISER,
        )
        self.assertTrue(organiser.can_edit_event)
        self.assertTrue(organiser.can_moderate_media)

    def test_co_organiser_permissions_are_disabled_by_default(self):
        event = self.create_event()

        organiser = add_co_organiser(
            event=event,
            actor=self.creator,
            user=self.other_user,
        )

        for permission in (
            "can_edit_event",
            "can_manage_participants",
            "can_manage_registrations",
            "can_change_visibility",
            "can_moderate_media",
            "can_delete_event",
        ):
            self.assertFalse(getattr(organiser, permission))

    def test_non_primary_organiser_cannot_add_co_organiser(self):
        event = self.create_event()

        with self.assertRaises(PermissionDenied):
            add_co_organiser(
                event=event,
                actor=self.other_user,
                user=self.third_user,
            )

        self.assertFalse(
            EventOrganiser.objects.filter(
                event=event,
                user=self.third_user,
            ).exists()
        )

    def test_primary_organiser_can_update_co_organiser_permissions(self):
        event = self.create_event()

        organiser = add_co_organiser(
            event=event,
            actor=self.creator,
            user=self.other_user,
            permissions={"can_edit_event": True},
        )

        updated = update_co_organiser_permissions(
            event=event,
            actor=self.creator,
            organiser_id=organiser.pk,
            permissions={
                "can_edit_event": False,
                "can_manage_participants": True,
            },
        )

        self.assertFalse(updated.can_edit_event)
        self.assertTrue(updated.can_manage_participants)

    def test_non_primary_organiser_cannot_update_permissions(self):
        event = self.create_event()

        organiser = add_co_organiser(
            event=event,
            actor=self.creator,
            user=self.third_user,
        )

        with self.assertRaises(PermissionDenied):
            update_co_organiser_permissions(
                event=event,
                actor=self.other_user,
                organiser_id=organiser.pk,
                permissions={"can_edit_event": True},
            )

        organiser.refresh_from_db()
        self.assertFalse(organiser.can_edit_event)

    def test_primary_organiser_can_remove_co_organiser(self):
        event = self.create_event()

        organiser = add_co_organiser(
            event=event,
            actor=self.creator,
            user=self.other_user,
        )

        remove_co_organiser(
            event=event,
            actor=self.creator,
            organiser_id=organiser.pk,
        )

        self.assertFalse(
            EventOrganiser.objects.filter(
                pk=organiser.pk
            ).exists()
        )

    def test_co_organiser_cannot_grant_permissions_to_themselves(self):
        event = self.create_event()

        organiser = add_co_organiser(
            event=event,
            actor=self.creator,
            user=self.other_user,
        )

        with self.assertRaises(PermissionDenied):
            update_co_organiser_permissions(
                event=event,
                actor=self.other_user,
                organiser_id=organiser.pk,
                permissions={"can_delete_event": True},
            )

        organiser.refresh_from_db()
        self.assertFalse(organiser.can_delete_event)


# ======================================================
# EVENT ORGANISER API TESTS
# ======================================================

class EventOrganiserAPITests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            email="api_creator@example.com",
            username="api_creator",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="api_other@example.com",
            username="api_other",
            password="TestPassword123!",
        )

        self.third_user = User.objects.create_user(
            email="api_third@example.com",
            username="api_third",
            password="TestPassword123!",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.creator)

        event_response = self.client.post(
            reverse("event-list-create"),
            {
                "title": "BYB Organiser API Test",
                "description": "Testing organiser endpoints.",
                "event_type": Event.EventType.SOCIAL,
                "category": "Technology",
                "starts_at": (
                    timezone.now() + timedelta(days=7)
                ).isoformat(),
                "visibility": Event.Visibility.PUBLIC,
                "city": "Lucknow",
            },
            format="json",
        )

        self.assertEqual(
            event_response.status_code,
            status.HTTP_201_CREATED,
            event_response.data,
        )

        self.event = Event.objects.get(
            pk=event_response.data["id"]
        )

        self.organisers_url = reverse(
            "event-organiser-list-create",
            kwargs={"event_id": self.event.id},
        )

    def get_organiser_detail_url(self, organiser):
        return reverse(
            "event-organiser-detail",
            kwargs={
                "event_id": self.event.id,
                "organiser_id": organiser.id,
            },
        )

    def add_co_organiser(self, user=None, permissions=None):
        response = self.client.post(
            self.organisers_url,
            {
                "user_id": str((user or self.other_user).id),
                "permissions": permissions or {},
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        return EventOrganiser.objects.get(
            pk=response.data["id"]
        )

    def test_primary_organiser_can_list_organisers(self):
        self.add_co_organiser()

        response = self.client.get(self.organisers_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 2)

    def test_primary_organiser_can_add_co_organiser_through_api(self):
        response = self.client.post(
            self.organisers_url,
            {
                "user_id": str(self.other_user.id),
                "permissions": {
                    "can_edit_event": True,
                    "can_moderate_media": True,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        organiser = EventOrganiser.objects.get(
            event=self.event,
            user=self.other_user,
        )

        self.assertEqual(
            organiser.role,
            EventOrganiser.Role.CO_ORGANISER,
        )
        self.assertTrue(organiser.can_edit_event)
        self.assertTrue(organiser.can_moderate_media)

    def test_ordinary_user_cannot_add_co_organiser(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.organisers_url,
            {
                "user_id": str(self.third_user.id),
                "permissions": {},
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            EventOrganiser.objects.filter(
                event=self.event,
                user=self.third_user,
            ).exists()
        )

    def test_primary_organiser_can_update_permissions_through_api(self):
        organiser = self.add_co_organiser()

        response = self.client.patch(
            self.get_organiser_detail_url(organiser),
            {
                "can_edit_event": True,
                "can_manage_participants": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        organiser.refresh_from_db()

        self.assertTrue(organiser.can_edit_event)
        self.assertTrue(organiser.can_manage_participants)

    def test_co_organiser_cannot_grant_themselves_permissions(self):
        organiser = self.add_co_organiser()

        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.get_organiser_detail_url(organiser),
            {"can_delete_event": True},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        organiser.refresh_from_db()
        self.assertFalse(organiser.can_delete_event)

    def test_primary_organiser_can_remove_co_organiser_through_api(self):
        organiser = self.add_co_organiser()

        response = self.client.delete(
            self.get_organiser_detail_url(organiser)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            EventOrganiser.objects.filter(
                pk=organiser.pk
            ).exists()
        )

    def test_co_organiser_without_visibility_permission_cannot_change_visibility(self):
        organiser = self.add_co_organiser(
            permissions={
                "can_edit_event": True,
                "can_change_visibility": False,
            }
        )

        self.client.force_authenticate(user=organiser.user)

        response = self.client.patch(
            reverse(
                "event-detail",
                kwargs={"event_id": self.event.id},
            ),
            {"visibility": Event.Visibility.PRIVATE},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.event.refresh_from_db()

        self.assertEqual(
            self.event.visibility,
            Event.Visibility.PUBLIC,
        )


# ======================================================
# EVENT PARTICIPANT SERVICE TESTS
# ======================================================

class EventParticipantServiceTests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            email="participant_creator@example.com",
            username="participant_creator",
            password="TestPassword123!",
        )

        self.user = User.objects.create_user(
            email="participant_user@example.com",
            username="participant_user",
            password="TestPassword123!",
        )

        self.second_user = User.objects.create_user(
            email="participant_second@example.com",
            username="participant_second",
            password="TestPassword123!",
        )

        self.co_organiser = User.objects.create_user(
            email="participant_coorganiser@example.com",
            username="participant_coorganiser",
            password="TestPassword123!",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.creator)

        self.event = self.create_event()

    def create_event(self, **overrides):
        data = {
            "title": "Participant Service Test Event",
            "description": "Testing Social event participation.",
            "event_type": Event.EventType.SOCIAL,
            "category": "Technology",
            "starts_at": (
                timezone.now() + timedelta(days=7)
            ).isoformat(),
            "visibility": Event.Visibility.PUBLIC,
            "city": "Lucknow",
        }

        data.update(overrides)

        response = self.client.post(
            reverse("event-list-create"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        return Event.objects.get(pk=response.data["id"])

    def get_participant(self, user, event=None):
        return EventParticipant.objects.get(
            event=event or self.event,
            user=user,
        )

    # --------------------------------------------------
    # Join request tests
    # --------------------------------------------------

    def test_user_can_request_to_join_public_social_event(self):
        participant = request_to_join_event(
            event=self.event,
            user=self.user,
        )

        self.assertEqual(
            participant.status,
            EventParticipant.Status.REQUESTED,
        )
        self.assertFalse(participant.can_upload_media)

    def test_user_cannot_request_to_join_selected_event(self):
        event = self.create_event(
            visibility=Event.Visibility.SELECTED,
        )

        with self.assertRaises(ValidationError):
            request_to_join_event(
                event=event,
                user=self.user,
            )

    def test_duplicate_join_request_is_rejected(self):
        request_to_join_event(
            event=self.event,
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            request_to_join_event(
                event=self.event,
                user=self.user,
            )

    def test_organiser_can_approve_join_request(self):
        participant = request_to_join_event(
            event=self.event,
            user=self.user,
        )

        approved = approve_join_request(
            event=self.event,
            actor=self.creator,
            participant_id=participant.pk,
        )

        self.assertEqual(
            approved.status,
            EventParticipant.Status.ACCEPTED,
        )
        self.assertTrue(approved.can_upload_media)
        self.assertIsNotNone(approved.joined_at)

    def test_organiser_can_decline_join_request(self):
        participant = request_to_join_event(
            event=self.event,
            user=self.user,
        )

        declined = decline_join_request(
            event=self.event,
            actor=self.creator,
            participant_id=participant.pk,
        )

        self.assertEqual(
            declined.status,
            EventParticipant.Status.DECLINED,
        )
        self.assertFalse(declined.can_upload_media)

    # --------------------------------------------------
    # Invitation tests
    # --------------------------------------------------

    def test_organiser_can_invite_user(self):
        participant = invite_to_event(
            event=self.event,
            actor=self.creator,
            user=self.user,
        )

        self.assertEqual(
            participant.status,
            EventParticipant.Status.INVITED,
        )
        self.assertEqual(participant.invited_by, self.creator)
        self.assertFalse(participant.can_upload_media)

    def test_invited_user_can_accept_invitation(self):
        invite_to_event(
            event=self.event,
            actor=self.creator,
            user=self.user,
        )

        participant = respond_to_invitation(
            event=self.event,
            user=self.user,
            accept=True,
        )

        self.assertEqual(
            participant.status,
            EventParticipant.Status.ACCEPTED,
        )
        self.assertTrue(participant.can_upload_media)

    def test_invited_user_can_decline_invitation(self):
        invite_to_event(
            event=self.event,
            actor=self.creator,
            user=self.user,
        )

        participant = respond_to_invitation(
            event=self.event,
            user=self.user,
            accept=False,
        )

        self.assertEqual(
            participant.status,
            EventParticipant.Status.DECLINED,
        )
        self.assertFalse(participant.can_upload_media)

    # --------------------------------------------------
    # Capacity tests
    # --------------------------------------------------

    def test_event_capacity_blocks_additional_acceptance(self):
        event = self.create_event(capacity=1)

        invite_to_event(
            event=event,
            actor=self.creator,
            user=self.user,
        )

        invite_to_event(
            event=event,
            actor=self.creator,
            user=self.second_user,
        )

        respond_to_invitation(
            event=event,
            user=self.user,
            accept=True,
        )

        with self.assertRaises(ValidationError):
            respond_to_invitation(
                event=event,
                user=self.second_user,
                accept=True,
            )

        second_participant = self.get_participant(
            self.second_user,
            event,
        )

        self.assertEqual(
            second_participant.status,
            EventParticipant.Status.INVITED,
        )

    def test_pending_requests_do_not_consume_capacity(self):
        event = self.create_event(capacity=1)

        request_to_join_event(
            event=event,
            user=self.user,
        )

        request_to_join_event(
            event=event,
            user=self.second_user,
        )

        participant = self.get_participant(
            self.user,
            event,
        )

        approved = approve_join_request(
            event=event,
            actor=self.creator,
            participant_id=participant.pk,
        )

        self.assertEqual(
            approved.status,
            EventParticipant.Status.ACCEPTED,
        )

    # --------------------------------------------------
    # Leaving and removal tests
    # --------------------------------------------------

    def test_accepted_participant_can_leave_event(self):
        invite_to_event(
            event=self.event,
            actor=self.creator,
            user=self.user,
        )

        respond_to_invitation(
            event=self.event,
            user=self.user,
            accept=True,
        )

        participant = leave_event(
            event=self.event,
            user=self.user,
        )

        self.assertEqual(
            participant.status,
            EventParticipant.Status.LEFT,
        )
        self.assertFalse(participant.can_upload_media)

    def test_organiser_can_remove_participant(self):
        invite_to_event(
            event=self.event,
            actor=self.creator,
            user=self.user,
        )

        accepted = respond_to_invitation(
            event=self.event,
            user=self.user,
            accept=True,
        )

        removed = remove_participant(
            event=self.event,
            actor=self.creator,
            participant_id=accepted.pk,
        )

        self.assertEqual(
            removed.status,
            EventParticipant.Status.REMOVED,
        )
        self.assertFalse(removed.can_upload_media)

    # --------------------------------------------------
    # Permission tests
    # --------------------------------------------------

    def test_co_organiser_with_permission_can_manage_participants(self):
        add_co_organiser(
            event=self.event,
            actor=self.creator,
            user=self.co_organiser,
            permissions={
                "can_manage_participants": True,
            },
        )

        participant = invite_to_event(
            event=self.event,
            actor=self.co_organiser,
            user=self.user,
        )

        self.assertEqual(
            participant.status,
            EventParticipant.Status.INVITED,
        )

    def test_co_organiser_without_permission_cannot_invite(self):
        add_co_organiser(
            event=self.event,
            actor=self.creator,
            user=self.co_organiser,
        )

        with self.assertRaises(PermissionDenied):
            invite_to_event(
                event=self.event,
                actor=self.co_organiser,
                user=self.user,
            )

    # --------------------------------------------------
    # Event type restrictions
    # --------------------------------------------------

    def test_personal_event_rejects_participant_requests(self):
        event = self.create_event(
            event_type=Event.EventType.PERSONAL,
        )

        with self.assertRaises(ValidationError):
            request_to_join_event(
                event=event,
                user=self.user,
            )

    def test_public_event_rejects_social_invitations(self):
        event = self.create_event(
            event_type=Event.EventType.PUBLIC,
        )

        with self.assertRaises(ValidationError):
            invite_to_event(
                event=event,
                actor=self.creator,
                user=self.user,
            )


# ======================================================
# EVENT REGISTRATION API TESTS
# ======================================================

class EventRegistrationAPITests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            email="registration_creator@example.com",
            username="registration_creator",
            password="TestPassword123!",
        )

        self.user = User.objects.create_user(
            email="registration_user@example.com",
            username="registration_user",
            password="TestPassword123!",
        )

        self.second_user = User.objects.create_user(
            email="registration_second@example.com",
            username="registration_second",
            password="TestPassword123!",
        )

        self.co_organiser = User.objects.create_user(
            email="registration_coorganiser@example.com",
            username="registration_coorganiser",
            password="TestPassword123!",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.creator)

        self.event = self.create_event()

    def create_event(self, **overrides):
        data = {
            "title": "BYB Public Registration Test",
            "description": "Testing public event registration.",
            "event_type": Event.EventType.PUBLIC,
            "category": "Technology",
            "starts_at": (
                timezone.now() + timedelta(days=7)
            ).isoformat(),
            "visibility": Event.Visibility.PUBLIC,
            "city": "Lucknow",
            "registration_enabled": True,
            "registration_mode": Event.RegistrationMode.AUTOMATIC,
        }

        data.update(overrides)

        response = self.client.post(
            reverse("event-list-create"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        return Event.objects.get(pk=response.data["id"])

    def get_registration_url(self, event=None):
        return reverse(
            "event-registration-list-create",
            kwargs={"event_id": (event or self.event).id},
        )

    def get_registration_me_url(self, event=None):
        return reverse(
            "event-registration-me",
            kwargs={"event_id": (event or self.event).id},
        )

    def get_registration_detail_url(self, registration):
        return reverse(
            "event-registration-detail",
            kwargs={
                "event_id": registration.event_id,
                "registration_id": registration.id,
            },
        )

    # --------------------------------------------------
    # Automatic registration
    # --------------------------------------------------

    def test_user_can_register_for_automatic_public_event(self):
        # The attendee must not be the event creator.
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_registration_url(),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        registration = EventRegistration.objects.get(
            event=self.event,
            user=self.user,
        )

        self.assertEqual(
            registration.status,
            EventRegistration.Status.CONFIRMED,
        )

    def test_registration_is_created_as_pending_in_approval_mode(self):
        event = self.create_event(
            registration_mode=Event.RegistrationMode.APPROVAL,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_registration_url(event),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        registration = EventRegistration.objects.get(
            event=event,
            user=self.user,
        )

        self.assertEqual(
            registration.status,
            EventRegistration.Status.PENDING,
        )

    # --------------------------------------------------
    # Cancellation
    # --------------------------------------------------

    def test_user_can_cancel_own_registration(self):
        self.client.force_authenticate(user=self.user)

        registration_response = self.client.post(
            self.get_registration_url(),
            {},
            format="json",
        )

        self.assertEqual(
            registration_response.status_code,
            status.HTTP_201_CREATED,
            registration_response.data,
        )

        response = self.client.delete(
            self.get_registration_me_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        registration = EventRegistration.objects.get(
            event=self.event,
            user=self.user,
        )

        self.assertEqual(
            registration.status,
            EventRegistration.Status.CANCELLED,
        )
        self.assertIsNotNone(registration.cancelled_at)

    # --------------------------------------------------
    # Organiser approval and rejection
    # --------------------------------------------------

    def create_pending_registration(self, user=None):
        user = user or self.user

        event = self.create_event(
            registration_mode=Event.RegistrationMode.APPROVAL,
        )

        self.client.force_authenticate(user=user)

        response = self.client.post(
            self.get_registration_url(event),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        return EventRegistration.objects.get(
            event=event,
            user=user,
        )

    def test_primary_organiser_can_approve_registration(self):
        registration = self.create_pending_registration()

        self.client.force_authenticate(user=self.creator)

        response = self.client.patch(
            self.get_registration_detail_url(registration),
            {"action": "approve"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        registration.refresh_from_db()

        self.assertEqual(
            registration.status,
            EventRegistration.Status.CONFIRMED,
        )

    def test_primary_organiser_can_reject_registration(self):
        registration = self.create_pending_registration()

        self.client.force_authenticate(user=self.creator)

        response = self.client.patch(
            self.get_registration_detail_url(registration),
            {"action": "reject"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        registration.refresh_from_db()

        self.assertEqual(
            registration.status,
            EventRegistration.Status.REJECTED,
        )

    # --------------------------------------------------
    # Registration management permissions
    # --------------------------------------------------

    def test_ordinary_user_cannot_list_all_registrations(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            self.get_registration_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_ordinary_user_cannot_approve_registration(self):
        registration = self.create_pending_registration()

        self.client.force_authenticate(user=self.second_user)

        response = self.client.patch(
            self.get_registration_detail_url(registration),
            {"action": "approve"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        registration.refresh_from_db()

        self.assertEqual(
            registration.status,
            EventRegistration.Status.PENDING,
        )

    def test_co_organiser_with_registration_permission_can_approve(self):
        registration = self.create_pending_registration()

        add_co_organiser(
            event=registration.event,
            actor=self.creator,
            user=self.co_organiser,
            permissions={
                "can_manage_registrations": True,
            },
        )

        self.client.force_authenticate(user=self.co_organiser)

        response = self.client.patch(
            self.get_registration_detail_url(registration),
            {"action": "approve"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        registration.refresh_from_db()

        self.assertEqual(
            registration.status,
            EventRegistration.Status.CONFIRMED,
        )

    # --------------------------------------------------
    # Capacity and registration restrictions
    # --------------------------------------------------

    def test_event_capacity_blocks_additional_registration(self):
        event = self.create_event(capacity=1)

        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.get_registration_url(event),
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
            first_response.data,
        )

        self.client.force_authenticate(user=self.second_user)

        second_response = self.client.post(
            self.get_registration_url(event),
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            EventRegistration.objects.filter(
                event=event,
                status=EventRegistration.Status.CONFIRMED,
            ).count(),
            1,
        )

    def test_disabled_registration_rejects_new_registration(self):
        event = self.create_event(
            registration_enabled=False,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_registration_url(event),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_closed_registration_window_rejects_registration(self):
        event = self.create_event(
            registration_closes_at=(
                timezone.now() - timedelta(hours=1)
            ).isoformat(),
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_registration_url(event),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_social_event_rejects_public_registration(self):
        event = self.create_event(
            event_type=Event.EventType.SOCIAL,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_registration_url(event),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

# ======================================================
# EVENT MEDIA UPLOAD PERMISSION TESTS
# ======================================================

class EventMediaUploadPermissionTests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            email="media_creator@example.com",
            username="media_creator",
            password="TestPassword123!",
        )

        self.user = User.objects.create_user(
            email="media_user@example.com",
            username="media_user",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="media_other@example.com",
            username="media_other",
            password="TestPassword123!",
        )

    def create_event(self, event_type, **overrides):
        return Event.objects.create(
            creator=self.creator,
            title="Media Permission Test",
            description="Testing media upload permissions.",
            event_type=event_type,
            category="Technology",
            starts_at=timezone.now() + timedelta(days=7),
            visibility=Event.Visibility.PUBLIC,
            **overrides,
        )

    # --------------------------------------------------
    # Personal event permissions
    # --------------------------------------------------

    def test_personal_event_creator_can_upload(self):
        event = self.create_event(Event.EventType.PERSONAL)

        self.assertTrue(
            can_upload_event_media(self.creator, event)
        )

    def test_authorised_personal_contributor_can_upload(self):
        event = self.create_event(Event.EventType.PERSONAL)

        EventParticipant.objects.create(
            event=event,
            user=self.user,
            status=EventParticipant.Status.INVITED,
            can_upload_media=True,
        )

        self.assertTrue(
            can_upload_event_media(self.user, event)
        )

    def test_unauthorised_personal_participant_cannot_upload(self):
        event = self.create_event(Event.EventType.PERSONAL)

        EventParticipant.objects.create(
            event=event,
            user=self.user,
            status=EventParticipant.Status.INVITED,
            can_upload_media=False,
        )

        self.assertFalse(
            can_upload_event_media(self.user, event)
        )

    # --------------------------------------------------
    # Social event permissions
    # --------------------------------------------------

    def test_accepted_social_participant_can_upload(self):
        event = self.create_event(Event.EventType.SOCIAL)

        EventParticipant.objects.create(
            event=event,
            user=self.user,
            status=EventParticipant.Status.ACCEPTED,
        )

        self.assertTrue(
            can_upload_event_media(self.user, event)
        )

    def test_pending_social_request_cannot_upload(self):
        event = self.create_event(Event.EventType.SOCIAL)

        EventParticipant.objects.create(
            event=event,
            user=self.user,
            status=EventParticipant.Status.REQUESTED,
        )

        self.assertFalse(
            can_upload_event_media(self.user, event)
        )

    def test_removed_social_participant_cannot_upload(self):
        event = self.create_event(Event.EventType.SOCIAL)

        EventParticipant.objects.create(
            event=event,
            user=self.user,
            status=EventParticipant.Status.REMOVED,
        )

        self.assertFalse(
            can_upload_event_media(self.user, event)
        )

    # --------------------------------------------------
    # Public event permissions
    # --------------------------------------------------

    def test_confirmed_public_attendee_can_upload(self):
        event = self.create_event(Event.EventType.PUBLIC)

        EventRegistration.objects.create(
            event=event,
            user=self.user,
            status=EventRegistration.Status.CONFIRMED,
        )

        self.assertTrue(
            can_upload_event_media(self.user, event)
        )

    def test_pending_public_registration_cannot_upload(self):
        event = self.create_event(Event.EventType.PUBLIC)

        EventRegistration.objects.create(
            event=event,
            user=self.user,
            status=EventRegistration.Status.PENDING,
        )

        self.assertFalse(
            can_upload_event_media(self.user, event)
        )

    def test_cancelled_public_registration_cannot_upload(self):
        event = self.create_event(Event.EventType.PUBLIC)

        EventRegistration.objects.create(
            event=event,
            user=self.user,
            status=EventRegistration.Status.CANCELLED,
        )

        self.assertFalse(
            can_upload_event_media(self.user, event)
        )

    # --------------------------------------------------
    # Organiser permissions
    # --------------------------------------------------

    def test_co_organiser_with_media_permission_can_upload(self):
        event = self.create_event(Event.EventType.SOCIAL)

        EventOrganiser.objects.create(
            event=event,
            user=self.user,
            role=EventOrganiser.Role.CO_ORGANISER,
            can_moderate_media=True,
        )

        self.assertTrue(
            can_upload_event_media(self.user, event)
        )

    def test_co_organiser_without_media_permission_cannot_upload(self):
        event = self.create_event(Event.EventType.SOCIAL)

        EventOrganiser.objects.create(
            event=event,
            user=self.user,
            role=EventOrganiser.Role.CO_ORGANISER,
            can_moderate_media=False,
        )

        self.assertFalse(
            can_upload_event_media(self.user, event)
        )

    # --------------------------------------------------
    # Event lifecycle restrictions
    # --------------------------------------------------

    def test_archived_event_rejects_new_media_uploads(self):
        event = self.create_event(
            Event.EventType.SOCIAL,
            status=Event.Status.ARCHIVED,
        )

        self.assertFalse(
            can_upload_event_media(self.creator, event)
        )

    def test_deleted_event_rejects_new_media_uploads(self):
        event = self.create_event(Event.EventType.SOCIAL)

        event.is_deleted = True
        event.deleted_at = timezone.now()
        event.deleted_by = self.creator
        event.save()

        self.assertFalse(
            can_upload_event_media(self.creator, event)
        )

    # --------------------------------------------------
    # Authentication restrictions
    # --------------------------------------------------

    def test_anonymous_user_cannot_upload(self):
        event = self.create_event(Event.EventType.SOCIAL)

        self.assertFalse(
            can_upload_event_media(None, event)
        )

    def test_unrelated_user_cannot_upload(self):
        event = self.create_event(Event.EventType.SOCIAL)

        self.assertFalse(
            can_upload_event_media(self.other_user, event)
        )