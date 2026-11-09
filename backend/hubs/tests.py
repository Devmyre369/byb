
'''
from django.test import TestCase

# Create your tests here.

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from hubs.models import Hub, HubMembership
from hubs.services.hub_service import create_hub


User = get_user_model()


class HubCreationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            username="hubowner",
            password="TestPassword123!",
        )

        self.hub_data = {
            "name": "Goel Coding Club",
            "hub_type": Hub.HubType.CLUB,
            "description": "A coding community.",
            "city": "Lucknow",
        }

    def test_hub_creation_assigns_creator_as_owner(self):
        hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        membership = HubMembership.objects.get(
            hub=hub,
            user=self.user,
        )

        self.assertEqual(hub.created_by, self.user)
        self.assertEqual(
            membership.role,
            HubMembership.Role.OWNER,
        )
        self.assertEqual(
            membership.status,
            HubMembership.Status.ACTIVE,
        )
        self.assertEqual(
            membership.source,
            HubMembership.Source.CREATION,
        )

    def test_hub_creation_generates_slug(self):
        hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        self.assertEqual(
            hub.slug,
            "goel-coding-club",
        )

    def test_duplicate_hub_names_generate_unique_slugs(self):
        first_hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        second_user = User.objects.create_user(
            email="owner2@example.com",
            username="hubowner2",
            password="TestPassword123!",
        )

        second_hub = create_hub(
            creator=second_user,
            hub_data=self.hub_data,
        )

        self.assertEqual(
            first_hub.slug,
            "goel-coding-club",
        )
        self.assertEqual(
            second_hub.slug,
            "goel-coding-club-2",
        )

    def test_creator_cannot_override_protected_fields(self):
        data = {
            **self.hub_data,
            "slug": "custom-untrusted-slug",
            "verification_status": Hub.VerificationStatus.VERIFIED,
            "created_by": None,
        }

        hub = create_hub(
            creator=self.user,
            hub_data=data,
        )

        self.assertEqual(
            hub.slug,
            "goel-coding-club",
        )
        self.assertEqual(
            hub.verification_status,
            Hub.VerificationStatus.UNVERIFIED,
        )
        self.assertEqual(
            hub.created_by,
            self.user,
        )

    def test_hub_creation_rolls_back_if_owner_creation_fails(self):
        with patch.object(
            HubMembership,
            "save",
            side_effect=RuntimeError("Simulated membership failure"),
        ):
            with self.assertRaises(RuntimeError):
                create_hub(
                    creator=self.user,
                    hub_data=self.hub_data,
                )

        self.assertEqual(Hub.objects.count(), 0)
        self.assertEqual(HubMembership.objects.count(), 0)
'''



from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import PermissionDenied, ValidationError

from hubs.models import Hub, HubMembership
from hubs.services.hub_service import create_hub
from hubs.services.membership_service import (
    approve_membership_request,
    invite_hub_member,
    leave_hub,
    reject_membership_request,
    remove_hub_member,
    request_to_join_hub,
)


User = get_user_model()


class HubCreationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            username="hubowner",
            password="TestPassword123!",
        )

        self.hub_data = {
            "name": "Goel Coding Club",
            "hub_type": Hub.HubType.CLUB,
            "description": "A coding community.",
            "city": "Lucknow",
        }

    def test_hub_creation_assigns_creator_as_owner(self):
        hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        membership = HubMembership.objects.get(
            hub=hub,
            user=self.user,
        )

        self.assertEqual(hub.created_by, self.user)
        self.assertEqual(membership.role, HubMembership.Role.OWNER)
        self.assertEqual(membership.status, HubMembership.Status.ACTIVE)
        self.assertEqual(membership.source, HubMembership.Source.CREATION)

    def test_hub_creation_generates_slug(self):
        hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        self.assertEqual(hub.slug, "goel-coding-club")

    def test_duplicate_hub_names_generate_unique_slugs(self):
        first_hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        second_user = User.objects.create_user(
            email="owner2@example.com",
            username="hubowner2",
            password="TestPassword123!",
        )

        second_hub = create_hub(
            creator=second_user,
            hub_data=self.hub_data,
        )

        self.assertEqual(first_hub.slug, "goel-coding-club")
        self.assertEqual(second_hub.slug, "goel-coding-club-2")

    def test_creator_cannot_override_protected_fields(self):
        data = {
            **self.hub_data,
            "slug": "custom-untrusted-slug",
            "verification_status": Hub.VerificationStatus.VERIFIED,
            "created_by": None,
        }

        hub = create_hub(
            creator=self.user,
            hub_data=data,
        )

        self.assertEqual(hub.slug, "goel-coding-club")
        self.assertEqual(
            hub.verification_status,
            Hub.VerificationStatus.UNVERIFIED,
        )
        self.assertEqual(hub.created_by, self.user)

    def test_hub_creation_rolls_back_if_owner_creation_fails(self):
        with patch.object(
            HubMembership,
            "save",
            side_effect=RuntimeError("Simulated membership failure"),
        ):
            with self.assertRaises(RuntimeError):
                create_hub(
                    creator=self.user,
                    hub_data=self.hub_data,
                )

        self.assertEqual(Hub.objects.count(), 0)
        self.assertEqual(HubMembership.objects.count(), 0)


class HubMembershipServiceTests(TestCase):

    def setUp(self):
        self.owner = self.create_user("owner")
        self.admin = self.create_user("admin")
        self.second_admin = self.create_user("secondadmin")
        self.editor = self.create_user("editor")
        self.member = self.create_user("member")
        self.new_user = self.create_user("newuser")

        self.hub = create_hub(
            creator=self.owner,
            hub_data={
                "name": "Membership Test Hub",
                "hub_type": Hub.HubType.CLUB,
                "description": "Testing membership operations.",
                "city": "Lucknow",
            },
        )

    def create_user(self, username):
        return User.objects.create_user(
            email=f"{username}@example.com",
            username=username,
            password="TestPassword123!",
        )

    def add_membership(self, user, role, status=HubMembership.Status.ACTIVE):
        return HubMembership.objects.create(
            hub=self.hub,
            user=user,
            role=role,
            status=status,
            source=HubMembership.Source.INVITATION,
            joined_at=None if status == HubMembership.Status.PENDING else self.hub.created_at,
        )

    def create_join_request(self, user=None):
        user = user or self.member
        return request_to_join_hub(
            user=user,
            hub=self.hub,
        )

    def test_approval_policy_creates_pending_request(self):
        membership = self.create_join_request()

        self.assertEqual(membership.status, HubMembership.Status.PENDING)
        self.assertEqual(membership.role, HubMembership.Role.MEMBER)
        self.assertEqual(membership.source, HubMembership.Source.REQUEST)
        self.assertIsNone(membership.joined_at)

    def test_automatic_policy_activates_membership(self):
        self.hub.membership_policy = Hub.MembershipPolicy.AUTOMATIC
        self.hub.save(update_fields=["membership_policy"])

        membership = self.create_join_request()

        self.assertEqual(membership.status, HubMembership.Status.ACTIVE)
        self.assertIsNotNone(membership.joined_at)

    def test_repeated_join_request_does_not_create_duplicate(self):
        first = self.create_join_request()
        second = self.create_join_request()

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(
            HubMembership.objects.filter(
                hub=self.hub,
                user=self.member,
            ).count(),
            1,
        )

    def test_owner_can_approve_join_request(self):
        request = self.create_join_request()

        approved = approve_membership_request(
            actor=self.owner,
            hub=self.hub,
            membership_id=request.pk,
        )

        self.assertEqual(approved.status, HubMembership.Status.ACTIVE)
        self.assertEqual(approved.reviewed_by, self.owner)
        self.assertIsNotNone(approved.reviewed_at)
        self.assertIsNotNone(approved.joined_at)

    def test_admin_can_reject_join_request(self):
        self.add_membership(self.admin, HubMembership.Role.ADMIN)
        request = self.create_join_request()

        rejected = reject_membership_request(
            actor=self.admin,
            hub=self.hub,
            membership_id=request.pk,
        )

        self.assertEqual(rejected.status, HubMembership.Status.REJECTED)
        self.assertEqual(rejected.reviewed_by, self.admin)
        self.assertIsNone(rejected.joined_at)

    def test_editor_cannot_approve_join_request(self):
        self.add_membership(self.editor, HubMembership.Role.EDITOR)
        request = self.create_join_request()

        with self.assertRaises(PermissionDenied):
            approve_membership_request(
                actor=self.editor,
                hub=self.hub,
                membership_id=request.pk,
            )

    def test_editor_cannot_invite_members(self):
        self.add_membership(self.editor, HubMembership.Role.EDITOR)

        with self.assertRaises(PermissionDenied):
            invite_hub_member(
                actor=self.editor,
                hub=self.hub,
                invited_user=self.new_user,
            )

    def test_admin_can_invite_member(self):
        self.add_membership(self.admin, HubMembership.Role.ADMIN)

        membership = invite_hub_member(
            actor=self.admin,
            hub=self.hub,
            invited_user=self.new_user,
        )

        self.assertEqual(membership.role, HubMembership.Role.MEMBER)
        self.assertEqual(membership.status, HubMembership.Status.ACTIVE)
        self.assertEqual(membership.source, HubMembership.Source.INVITATION)
        self.assertEqual(membership.invited_by, self.admin)
        self.assertEqual(membership.reviewed_by, self.admin)

    def test_invitation_does_not_grant_admin_role(self):
        membership = invite_hub_member(
            actor=self.owner,
            hub=self.hub,
            invited_user=self.new_user,
        )

        self.assertEqual(membership.role, HubMembership.Role.MEMBER)

    def test_member_can_leave_hub(self):
        membership = self.add_membership(
            self.member,
            HubMembership.Role.MEMBER,
        )

        result = leave_hub(
            user=self.member,
            hub=self.hub,
        )

        self.assertTrue(result)
        self.assertFalse(
            HubMembership.objects.filter(pk=membership.pk).exists()
        )

    def test_owner_cannot_leave_hub(self):
        with self.assertRaises(ValidationError):
            leave_hub(
                user=self.owner,
                hub=self.hub,
            )

        self.assertTrue(
            HubMembership.objects.filter(
                hub=self.hub,
                user=self.owner,
                role=HubMembership.Role.OWNER,
            ).exists()
        )

    def test_owner_cannot_be_removed(self):
        owner_membership = HubMembership.objects.get(
            hub=self.hub,
            user=self.owner,
        )

        with self.assertRaises(PermissionDenied):
            remove_hub_member(
                actor=self.owner,
                hub=self.hub,
                membership_id=owner_membership.pk,
            )

    def test_admin_cannot_remove_another_admin(self):
        self.add_membership(self.admin, HubMembership.Role.ADMIN)
        second_admin_membership = self.add_membership(
            self.second_admin,
            HubMembership.Role.ADMIN,
        )

        with self.assertRaises(PermissionDenied):
            remove_hub_member(
                actor=self.admin,
                hub=self.hub,
                membership_id=second_admin_membership.pk,
            )

        self.assertTrue(
            HubMembership.objects.filter(
                pk=second_admin_membership.pk
            ).exists()
        )

    def test_admin_can_remove_editor(self):
        self.add_membership(self.admin, HubMembership.Role.ADMIN)
        editor_membership = self.add_membership(
            self.editor,
            HubMembership.Role.EDITOR,
        )

        result = remove_hub_member(
            actor=self.admin,
            hub=self.hub,
            membership_id=editor_membership.pk,
        )

        self.assertTrue(result)
        self.assertFalse(
            HubMembership.objects.filter(pk=editor_membership.pk).exists()
        )

    def test_member_cannot_remove_another_member(self):
        self.add_membership(self.member, HubMembership.Role.MEMBER)
        target = self.add_membership(
            self.new_user,
            HubMembership.Role.MEMBER,
        )

        with self.assertRaises(PermissionDenied):
            remove_hub_member(
                actor=self.member,
                hub=self.hub,
                membership_id=target.pk,
            )

    def test_user_cannot_leave_hub_without_membership(self):
        with self.assertRaises(ValidationError):
            leave_hub(
                user=self.new_user,
                hub=self.hub,
            )



from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient


class HubAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.owner = self.create_user("apiowner")
        self.admin = self.create_user("apiadmin")
        self.second_admin = self.create_user("apisecondadmin")
        self.editor = self.create_user("apieditor")
        self.member = self.create_user("apimember")
        self.new_user = self.create_user("apinewuser")

        self.hub = create_hub(
            creator=self.owner,
            hub_data={
                "name": "API Test Hub",
                "hub_type": Hub.HubType.CLUB,
                "description": "Testing Hub API endpoints.",
                "city": "Lucknow",
            },
        )

        self.hub_url = reverse(
            "hub-detail",
            kwargs={"hub_id": self.hub.id},
        )

        self.membership_url = reverse(
            "hub-membership-me",
            kwargs={"hub_id": self.hub.id},
        )

        self.members_url = reverse(
            "hub-member-list-create",
            kwargs={"hub_id": self.hub.id},
        )

        self.requests_url = reverse(
            "hub-membership-requests",
            kwargs={"hub_id": self.hub.id},
        )

    def create_user(self, username):
        return User.objects.create_user(
            email=f"{username}@example.com",
            username=username,
            password="TestPassword123!",
        )

    def add_membership(self, user, role):
        return HubMembership.objects.create(
            hub=self.hub,
            user=user,
            role=role,
            status=HubMembership.Status.ACTIVE,
            source=HubMembership.Source.INVITATION,
            joined_at=timezone.now(),
        )

    def create_pending_request(self, user=None):
        return request_to_join_hub(
            user=user or self.member,
            hub=self.hub,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    # --------------------------------------------------
    # Public Hub endpoints
    # --------------------------------------------------

    def test_anonymous_user_can_discover_hubs(self):
        response = self.client.get(
            reverse("hub-list-create")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_can_view_hub_details(self):
        response = self.client.get(self.hub_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.hub.name)

    def test_anonymous_user_cannot_create_hub(self):
        response = self.client.post(
            reverse("hub-list-create"),
            {
                "name": "Unauthorized Hub",
                "hub_type": Hub.HubType.CLUB,
                "description": "Should not be created.",
                "city": "Lucknow",
            },
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))
        self.assertFalse(
            Hub.objects.filter(name="Unauthorized Hub").exists()
        )

    def test_anonymous_user_can_view_active_members(self):
        self.add_membership(
            self.member,
            HubMembership.Role.MEMBER,
        )

        response = self.client.get(self.members_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --------------------------------------------------
    # Membership endpoints
    # --------------------------------------------------

    def test_authenticated_user_can_submit_join_request(self):
        self.authenticate(self.new_user)

        response = self.client.post(
            self.membership_url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["membership"]["status"],
            HubMembership.Status.PENDING,
        )

    def test_automatic_policy_activates_membership_through_api(self):
        self.hub.membership_policy = Hub.MembershipPolicy.AUTOMATIC
        self.hub.save(update_fields=["membership_policy"])

        self.authenticate(self.new_user)

        response = self.client.post(
            self.membership_url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["membership"]["status"],
            HubMembership.Status.ACTIVE,
        )

    def test_user_can_view_own_membership(self):
        self.add_membership(
            self.member,
            HubMembership.Role.MEMBER,
        )

        self.authenticate(self.member)

        response = self.client.get(self.membership_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["membership"]["role"],
            HubMembership.Role.MEMBER,
        )

    def test_anonymous_user_cannot_join_hub(self):
        response = self.client.post(
            self.membership_url,
            {},
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))

    # --------------------------------------------------
    # Membership request management
    # --------------------------------------------------

    def test_owner_can_view_pending_requests(self):
        self.create_pending_request()

        self.authenticate(self.owner)

        response = self.client.get(self.requests_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_editor_cannot_view_pending_requests(self):
        self.add_membership(
            self.editor,
            HubMembership.Role.EDITOR,
        )
        self.create_pending_request()

        self.authenticate(self.editor)

        response = self.client.get(self.requests_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_approve_request_through_api(self):
        membership = self.create_pending_request()

        self.authenticate(self.owner)

        response = self.client.patch(
            reverse(
                "hub-membership-detail",
                kwargs={
                    "hub_id": self.hub.id,
                    "membership_id": membership.id,
                },
            ),
            {"action": "approve"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["status"],
            HubMembership.Status.ACTIVE,
        )

    def test_public_member_list_does_not_expose_pending_requests(self):
        self.create_pending_request()

        response = self.client.get(self.members_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_user_ids = [
            item["user_id"]
            for item in response.data
        ]

        self.assertNotIn(
            str(self.member.id),
            returned_user_ids,
        )

    # --------------------------------------------------
    # Role restrictions
    # --------------------------------------------------

    def test_admin_cannot_remove_another_admin_through_api(self):
        self.add_membership(
            self.admin,
            HubMembership.Role.ADMIN,
        )

        target = self.add_membership(
            self.second_admin,
            HubMembership.Role.ADMIN,
        )

        self.authenticate(self.admin)

        response = self.client.delete(
            reverse(
                "hub-membership-detail",
                kwargs={
                    "hub_id": self.hub.id,
                    "membership_id": target.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            HubMembership.objects.filter(pk=target.pk).exists()
        )

    def test_owner_cannot_leave_through_api(self):
        self.authenticate(self.owner)

        response = self.client.delete(self.membership_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            HubMembership.objects.filter(
                hub=self.hub,
                user=self.owner,
                role=HubMembership.Role.OWNER,
            ).exists()
        )
